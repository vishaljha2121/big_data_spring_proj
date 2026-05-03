#!/usr/bin/env python3
"""Consume and validate a sample of Kafka replay events."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import jsonschema


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstrap-servers", default="localhost:9092")
    parser.add_argument("--topic", default="tennis-point-events")
    parser.add_argument("--schema", type=Path, default=Path("contracts/point_event_schema.json"))
    parser.add_argument("--max-events", type=int, default=100)
    parser.add_argument("--group-id", default="spark-tennis-validation")
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
    for message in consumer:
        count += 1
        try:
            jsonschema.validate(message.value, schema)
        except Exception as exc:
            errors.append({"offset": message.offset, "error": str(exc)})
        if count >= args.max_events:
            break
    consumer.close()
    print(json.dumps({"status": "PASSED" if not errors and count else "FAILED", "events_checked": count, "errors": errors[:5]}, indent=2))
    if errors or count == 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
