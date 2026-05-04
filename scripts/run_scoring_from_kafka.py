#!/usr/bin/env python3
"""Optional Kafka consumer scorer for canonical replay point events."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from streaming.stream_scorer import StreamScorer


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstrap-servers", default="localhost:9092")
    parser.add_argument("--topic", default="tennis-point-events")
    parser.add_argument("--consumer-group", default="scoring-smoke-test")
    parser.add_argument("--odds-latest", type=Path, default=Path("data/models/odds/latest.json"))
    parser.add_argument("--risk-latest", type=Path, default=Path("data/models/risk/latest.json"))
    parser.add_argument("--output-jsonl", type=Path, required=True)
    parser.add_argument("--max-events", type=int, default=100)
    parser.add_argument("--timeout-seconds", type=int, default=30)
    args = parser.parse_args()
    try:
        from kafka import KafkaConsumer
    except ImportError as exc:
        raise SystemExit("Kafka scoring requires kafka-python. Install requirements.txt first.") from exc

    scorer = StreamScorer(args.odds_latest, args.risk_latest)
    consumer = KafkaConsumer(
        args.topic,
        bootstrap_servers=args.bootstrap_servers,
        group_id=args.consumer_group,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        consumer_timeout_ms=1000,
    )
    args.output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    deadline = time.time() + args.timeout_seconds
    with args.output_jsonl.open("w", encoding="utf-8") as handle:
        while count < args.max_events and time.time() < deadline:
            for message in consumer:
                scored = scorer.score_event(message.value)
                handle.write(json.dumps(scored, sort_keys=True, separators=(",", ":")) + "\n")
                count += 1
                if count >= args.max_events:
                    break
    consumer.close()
    if count == 0:
        raise SystemExit("No Kafka events were scored")
    print(f"Kafka scorer wrote {count} scored events to {args.output_jsonl}")


if __name__ == "__main__":
    main()
