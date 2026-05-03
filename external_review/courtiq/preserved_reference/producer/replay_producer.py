import argparse
import json
import time

import pandas as pd
from jsonschema import Draft202012Validator, ValidationError
from kafka import KafkaProducer


def load_schema(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def make_validator(path):
    return Draft202012Validator(load_schema(path))


def to_jsonable(value):
    if pd.isna(value):
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value.item() if hasattr(value, "item") else value


def row_to_manifest_record(row):
    return {column: to_jsonable(value) for column, value in row.items()}


def parse_match_metadata(source_match_id):
    if not source_match_id:
        return None, None

    parts = source_match_id.split("-", 2)
    if len(parts) < 2:
        return None, None

    year = int(parts[0]) if parts[0].isdigit() else None
    slam = parts[1] or None
    return year, slam


def manifest_to_point_event(manifest_record):
    year, slam = parse_match_metadata(manifest_record.get("source_match_id"))

    return {
        "event_id": manifest_record.get("event_id"),
        "match_id": manifest_record.get("source_match_id")
        or manifest_record.get("synthetic_match_id"),
        "source_match_id": manifest_record.get("source_match_id"),
        "event_index": manifest_record.get("event_index"),
        "year": year,
        "slam": slam,
        "tournament": None,
        "surface": None,
        "player_a": manifest_record.get("player_a"),
        "player_b": manifest_record.get("player_b"),
        "server_player": manifest_record.get("server_player"),
        "receiver_player": manifest_record.get("receiver_player"),
        "point_winner_player": manifest_record.get("point_winner_player"),
        "set_number": manifest_record.get("set_number"),
        "game_number": manifest_record.get("game_number"),
        "point_number": manifest_record.get("point_number"),
        "p1_score": manifest_record.get("p1_score"),
        "p2_score": manifest_record.get("p2_score"),
        "p1_games_won": None,
        "p2_games_won": None,
        "rally_length": None,
        "serve_speed_kmh": None,
        "serve_speed_mph": None,
        "is_ace": manifest_record.get("is_ace"),
        "is_double_fault": manifest_record.get("is_double_fault"),
        "is_break_point": manifest_record.get("is_break_point"),
        "elapsed_seconds": manifest_record.get("replay_offset_seconds"),
        "source_file": manifest_record.get("source_file"),
        "schema_version": manifest_record.get("replay_schema_version"),
        "replay_session_id": manifest_record.get("replay_session_id"),
        "synthetic_match_id": manifest_record.get("synthetic_match_id"),
        "event_ts": manifest_record.get("event_ts"),
    }


def build_dlq_event(stage, error_message, manifest_record, point_event=None):
    event = {
        "stage": stage,
        "error": error_message,
        "raw_event": manifest_record,
    }
    if point_event is not None:
        event["point_event"] = point_event
    return event


def make_producer(bootstrap_servers):
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: str(k).encode("utf-8"),
        retries=5,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--schema", default="contracts/replay_manifest_schema.json")
    parser.add_argument("--point-event-schema", default="contracts/point_event_schema.json")
    parser.add_argument("--bootstrap-servers", default="localhost:9092")
    parser.add_argument("--topic", default="tennis.replay.manifest")
    parser.add_argument("--dlq-topic", default="tennis.replay.manifest.dlq")
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    manifest_validator = make_validator(args.schema)
    point_event_validator = make_validator(args.point_event_schema)

    df = pd.read_parquet(args.manifest)

    if "replay_order" in df.columns:
        df = df.sort_values("replay_order")

    if args.limit:
        df = df.head(args.limit)

    producer = None if args.dry_run else make_producer(args.bootstrap_servers)

    valid_count = 0
    dlq_count = 0
    previous_offset = None

    for _, row in df.iterrows():
        manifest_record = row_to_manifest_record(row)
        valid = False
        event_to_publish = None

        try:
            manifest_validator.validate(manifest_record)
        except ValidationError as e:
            event_to_publish = build_dlq_event(
                stage="manifest_row",
                error_message=e.message,
                manifest_record=manifest_record,
            )
        else:
            point_event = manifest_to_point_event(manifest_record)
            try:
                point_event_validator.validate(point_event)
                valid = True
                event_to_publish = point_event
            except ValidationError as e:
                event_to_publish = build_dlq_event(
                    stage="point_event",
                    error_message=e.message,
                    manifest_record=manifest_record,
                    point_event=point_event,
                )

        if args.dry_run:
            print(json.dumps(event_to_publish, indent=2)[:1000])
            if valid:
                valid_count += 1
            else:
                dlq_count += 1
        else:
            if valid:
                producer.send(
                    args.topic,
                    key=event_to_publish.get("synthetic_match_id")
                    or event_to_publish.get("source_match_id"),
                    value=event_to_publish,
                )
                valid_count += 1
            else:
                producer.send(
                    args.dlq_topic,
                    key="invalid",
                    value=event_to_publish,
                )
                dlq_count += 1

        if "replay_offset_seconds" in row and args.speed > 0:
            current_offset = row["replay_offset_seconds"]
            if previous_offset is not None:
                delay = max(0, (current_offset - previous_offset) / args.speed)
                if delay > 0:
                    time.sleep(delay)
            previous_offset = current_offset

    if producer:
        producer.flush()
        producer.close()

    print("Replay complete")
    print("Valid events:", valid_count)
    print("DLQ events:", dlq_count)


if __name__ == "__main__":
    main()
