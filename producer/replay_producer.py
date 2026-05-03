#!/usr/bin/env python3
"""Replay canonical manifest rows as point-event JSON or Kafka messages."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

import jsonschema
import pandas as pd

try:
    from config import load_topic_config
except ImportError:  # pragma: no cover - used when imported as producer.replay_producer
    from producer.config import load_topic_config


REQUIRED_MANIFEST_COLUMNS = [
    "replay_session_id",
    "synthetic_match_id",
    "source_match_id",
    "event_id",
    "synthetic_event_id",
    "event_index",
    "replay_order",
    "replay_offset_seconds",
    "event_ts",
    "player_a",
    "player_b",
    "server_player",
    "receiver_player",
    "point_winner_player",
    "set_number",
    "game_number",
    "point_number",
    "p1_score",
    "p2_score",
    "is_ace",
    "is_double_fault",
    "is_break_point",
    "source_file",
]


def load_schema(path: Path = Path("contracts/point_event_schema.json")) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def to_jsonable(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def manifest_row_to_event(row: Dict[str, Any]) -> Dict[str, Any]:
    event = {"schema_version": "point_event_v1"}
    for column in REQUIRED_MANIFEST_COLUMNS:
        event[column] = to_jsonable(row.get(column))
    return event


def load_manifest(path: Path, max_events: int | None, max_matches: int | None, seed: int) -> pd.DataFrame:
    df = pd.read_parquet(path)
    missing = [col for col in REQUIRED_MANIFEST_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"manifest missing required columns: {missing}")
    df = df.sort_values(["synthetic_match_id", "replay_order", "synthetic_event_id"], kind="mergesort")
    if max_matches is not None:
        match_ids = pd.Series(df["synthetic_match_id"].dropna().unique()).sort_values().sample(
            n=min(max_matches, df["synthetic_match_id"].nunique()),
            random_state=seed,
        )
        df = df[df["synthetic_match_id"].isin(set(match_ids))]
        df = df.sort_values(["synthetic_match_id", "replay_order", "synthetic_event_id"], kind="mergesort")
    if max_events is not None:
        df = df.head(max_events)
    return df


def validate_event(event: Dict[str, Any], schema: Dict[str, Any]) -> None:
    jsonschema.validate(event, schema)


def iter_events(df: pd.DataFrame, schema: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    for record in df.to_dict(orient="records"):
        event = manifest_row_to_event(record)
        validate_event(event, schema)
        yield event


def kafka_producer(bootstrap_servers: str):
    try:
        from kafka import KafkaProducer
    except ImportError as exc:
        raise SystemExit("Kafka mode requires kafka-python. Install requirements.txt first.") from exc
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        key_serializer=lambda value: str(value).encode("utf-8"),
        value_serializer=lambda value: json.dumps(value, separators=(",", ":")).encode("utf-8"),
        retries=5,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("data/replay/manifests/replay_manifest_v1.parquet"))
    parser.add_argument("--config", type=Path, default=Path("infra/kafka/topic_config.json"))
    parser.add_argument("--bootstrap-servers", default="localhost:9092")
    parser.add_argument("--topic", default=None)
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--max-events", type=int, default=None)
    parser.add_argument("--max-matches", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--dry-run-output", type=Path, default=Path("data/results/replay_dry_run/sample_events.jsonl"))
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    topic_config = load_topic_config(args.config)
    topic = args.topic or topic_config["topic"]
    schema = load_schema()
    df = load_manifest(args.manifest, args.max_events, args.max_matches, args.seed)
    events = list(iter_events(df, schema))
    if args.validate_only:
        print(f"Validated {len(events)} replay events")
        return
    if args.dry_run:
        args.dry_run_output.parent.mkdir(parents=True, exist_ok=True)
        with args.dry_run_output.open("w", encoding="utf-8") as handle:
            for event in events:
                handle.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")
        print(f"Dry-run wrote {len(events)} events to {args.dry_run_output}")
        return
    producer = kafka_producer(args.bootstrap_servers)
    previous_offset = None
    produced = 0
    invalid = 0
    for event in events:
        try:
            key = event[topic_config["partition_key"]]
            producer.send(topic, key=key, value=event)
            produced += 1
            current_offset = event["replay_offset_seconds"]
            if previous_offset is not None and args.speed > 0:
                delay = max(0.0, (current_offset - previous_offset) / args.speed)
                if delay:
                    time.sleep(delay)
            previous_offset = current_offset
        except Exception as exc:
            invalid += 1
            print(f"invalid or failed event {event.get('synthetic_event_id')}: {exc}", file=sys.stderr)
    producer.flush()
    producer.close()
    print(f"Kafka replay complete: produced={produced} invalid={invalid} topic={topic}")
    if invalid:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
