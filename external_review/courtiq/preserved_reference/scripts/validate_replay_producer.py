import argparse
import json
from pathlib import Path
import sys
from uuid import uuid4

from kafka import KafkaConsumer
from jsonschema import Draft202012Validator, ValidationError


DLQ_EVENT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "stage": {
            "type": "string",
            "enum": ["manifest_row", "point_event"],
        },
        "error": {"type": "string"},
        "raw_event": {"type": "object"},
        "point_event": {"type": "object"},
    },
    "required": ["stage", "error", "raw_event"],
}


def load_schema(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def make_validator(path):
    return Draft202012Validator(load_schema(path))


def make_dlq_validator():
    return Draft202012Validator(DLQ_EVENT_SCHEMA)


def make_run_group_id(group_id):
    return f"{group_id}-{uuid4().hex}"


def make_consumer(
    topic,
    bootstrap_servers,
    group_id,
    from_beginning=True,
    consumer_timeout_ms=5000,
):
    return KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        auto_offset_reset="earliest" if from_beginning else "latest",
        enable_auto_commit=False,
        group_id=group_id,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        consumer_timeout_ms=consumer_timeout_ms,
    )


def extract_replay_session_id(event):
    if not isinstance(event, dict):
        return None

    replay_session_id = event.get("replay_session_id")
    if replay_session_id:
        return replay_session_id

    raw_event = event.get("raw_event")
    if isinstance(raw_event, dict) and raw_event.get("replay_session_id"):
        return raw_event["replay_session_id"]

    point_event = event.get("point_event")
    if isinstance(point_event, dict) and point_event.get("replay_session_id"):
        return point_event["replay_session_id"]

    return None


def event_matches_replay_session(event, replay_session_id):
    if replay_session_id is None:
        return True
    return extract_replay_session_id(event) == replay_session_id


def validate_topic(
    topic,
    validator,
    bootstrap_servers,
    limit,
    group_id,
    replay_session_id=None,
):
    consumer = make_consumer(
        topic=topic,
        bootstrap_servers=bootstrap_servers,
        group_id=make_run_group_id(group_id),
    )

    total_seen = 0
    total_checked = 0
    valid = 0
    invalid = 0
    errors = []

    for message in consumer:
        event = message.value
        total_seen += 1

        if not event_matches_replay_session(event, replay_session_id):
            continue

        total_checked += 1

        try:
            validator.validate(event)
            valid += 1
        except ValidationError as e:
            invalid += 1
            errors.append({
                "offset": message.offset,
                "partition": message.partition,
                "error": e.message,
                "event": event,
            })

        if limit and total_checked >= limit:
            break

    consumer.close()

    return {
        "topic": topic,
        "replay_session_id": replay_session_id,
        "total_messages_seen": total_seen,
        "total_messages_checked": total_checked,
        "valid_messages": valid,
        "invalid_messages": invalid,
        "errors": errors[:5],
    }


def count_dlq(
    topic,
    bootstrap_servers,
    limit,
    group_id,
    replay_session_id=None,
    validator=None,
):
    consumer = make_consumer(
        topic=topic,
        bootstrap_servers=bootstrap_servers,
        group_id=make_run_group_id(group_id),
    )

    total_seen = 0
    total_checked = 0
    valid_dlq_messages = 0
    invalid_dlq_messages = 0
    samples = []
    errors = []

    dlq_validator = validator or make_dlq_validator()

    for message in consumer:
        total_seen += 1
        event = message.value

        if not event_matches_replay_session(event, replay_session_id):
            continue

        total_checked += 1

        try:
            dlq_validator.validate(event)
            valid_dlq_messages += 1
        except ValidationError as e:
            invalid_dlq_messages += 1
            errors.append(
                {
                    "offset": message.offset,
                    "partition": message.partition,
                    "error": e.message,
                    "event": event,
                }
            )

        if len(samples) < 5:
            samples.append(event)

        if limit and total_checked >= limit:
            break

    consumer.close()

    return {
        "topic": topic,
        "replay_session_id": replay_session_id,
        "total_messages_seen": total_seen,
        "dlq_messages_checked": total_checked,
        "valid_dlq_messages": valid_dlq_messages,
        "invalid_dlq_messages": invalid_dlq_messages,
        "errors": errors[:5],
        "sample_dlq_messages": samples,
    }


def build_final_report(event_result, dlq_result, fail_on_dlq=True):
    failure_reasons = []

    if event_result["total_messages_checked"] == 0:
        failure_reasons.append("No matching event messages were validated.")
    if event_result["invalid_messages"] > 0:
        failure_reasons.append(
            f'{event_result["invalid_messages"]} event message(s) failed schema validation.'
        )
    if dlq_result["invalid_dlq_messages"] > 0:
        failure_reasons.append(
            f'{dlq_result["invalid_dlq_messages"]} DLQ message(s) failed envelope validation.'
        )
    if fail_on_dlq and dlq_result["dlq_messages_checked"] > 0:
        failure_reasons.append(
            f'{dlq_result["dlq_messages_checked"]} DLQ message(s) were found.'
        )

    return {
        "overall_status": "passed" if not failure_reasons else "failed",
        "failure_reasons": failure_reasons,
        "event_topic_validation": event_result,
        "dlq_topic_check": dlq_result,
    }


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--bootstrap-servers", default="localhost:9092")
    parser.add_argument("--topic", default="tennis.point.events")
    parser.add_argument("--dlq-topic", default="tennis.point.events.dlq")
    parser.add_argument("--schema", default="contracts/point_event_schema.json")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--group-id", default="replay-validator")
    parser.add_argument("--output", default="docs/replay_validation_report.json")
    parser.add_argument("--replay-session-id", default=None)
    parser.add_argument("--allow-dlq", action="store_true")

    args = parser.parse_args()

    validator = make_validator(args.schema)

    result = validate_topic(
        topic=args.topic,
        validator=validator,
        bootstrap_servers=args.bootstrap_servers,
        limit=args.limit,
        group_id=args.group_id,
        replay_session_id=args.replay_session_id,
    )

    dlq_result = count_dlq(
        topic=args.dlq_topic,
        bootstrap_servers=args.bootstrap_servers,
        limit=args.limit,
        group_id=args.group_id + "-dlq",
        replay_session_id=args.replay_session_id,
    )

    final_report = build_final_report(
        event_result=result,
        dlq_result=dlq_result,
        fail_on_dlq=not args.allow_dlq,
    )

    print(json.dumps(final_report, indent=2))

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2)

    print(f"\nSaved validation report to {output_path}")
    if final_report["overall_status"] == "failed":
        print(
            "Validation failed: " + "; ".join(final_report["failure_reasons"]),
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
