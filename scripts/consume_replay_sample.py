#!/usr/bin/env python3
"""Consume and validate a sample of Kafka replay events."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import jsonschema


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_report(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstrap-servers", default="localhost:9092")
    parser.add_argument("--topic", default="tennis-point-events")
    parser.add_argument("--schema", type=Path, default=Path("contracts/point_event_schema.json"))
    parser.add_argument("--max-events", type=int, default=100)
    parser.add_argument("--group-id", default="spark-tennis-validation")
    parser.add_argument("--report", type=Path, default=Path("data/results/kafka_runtime/kafka_consume_sample_report.json"))
    args = parser.parse_args()
    try:
        from kafka import KafkaConsumer
    except ImportError as exc:
        raise SystemExit("Kafka sample consumer requires kafka-python. Install requirements.txt first.") from exc
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    consumer = KafkaConsumer(
        args.topic,
        bootstrap_servers=args.bootstrap_servers,
        group_id=args.group_id,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        consumer_timeout_ms=10000,
    )
    count = 0
    errors = []
    synthetic_match_missing = 0
    synthetic_event_ids = set()
    duplicate_synthetic_event_ids = 0
    for message in consumer:
        count += 1
        try:
            jsonschema.validate(message.value, schema)
            if not message.value.get("synthetic_match_id"):
                synthetic_match_missing += 1
            event_id = message.value.get("synthetic_event_id")
            if event_id in synthetic_event_ids:
                duplicate_synthetic_event_ids += 1
            if event_id:
                synthetic_event_ids.add(event_id)
        except Exception as exc:
            errors.append({"offset": message.offset, "error": str(exc)})
        if count >= args.max_events:
            break
    consumer.close()
    status = "PASSED" if not errors and count >= args.max_events and synthetic_match_missing == 0 else "FAILED"
    report = {
        "generated_at": now_iso(),
        "status": status,
        "bootstrap_servers": args.bootstrap_servers,
        "topic": args.topic,
        "events_checked": count,
        "expected_events": args.max_events,
        "synthetic_match_missing": synthetic_match_missing,
        "duplicate_synthetic_event_ids": duplicate_synthetic_event_ids,
        "errors": errors[:5],
    }
    write_report(args.report, report)
    print(json.dumps(report, indent=2))
    if status != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
