#!/usr/bin/env python3
"""Validate replay producer JSONL dry-run output."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

import jsonschema


MODEL_FEATURE_PREFIXES = ("player_a_point_win_pct_before", "server_point_win_pct_before", "label_", "rally_length_avg_before")


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--schema", type=Path, default=Path("contracts/point_event_schema.json"))
    parser.add_argument("--report", type=Path, default=Path("data/results/replay_dry_run/validation_report.json"))
    args = parser.parse_args()
    schema = read_json(args.schema)
    errors: List[str] = []
    seen_ids = set()
    orders = defaultdict(list)
    offsets = defaultdict(list)
    count = 0
    with args.events.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            count += 1
            event = json.loads(line)
            try:
                jsonschema.validate(event, schema)
            except Exception as exc:
                errors.append(f"line {line_no}: schema error: {exc}")
                continue
            synthetic_event_id = event["synthetic_event_id"]
            if synthetic_event_id in seen_ids:
                errors.append(f"duplicate synthetic_event_id: {synthetic_event_id}")
            seen_ids.add(synthetic_event_id)
            if not event.get("event_id") or not event.get("synthetic_match_id"):
                errors.append(f"line {line_no}: missing event_id or synthetic_match_id")
            if any(key.startswith(MODEL_FEATURE_PREFIXES) for key in event):
                errors.append(f"line {line_no}: model feature leaked into raw event")
            match_id = event["synthetic_match_id"]
            orders[match_id].append(event["replay_order"])
            offsets[match_id].append(event["replay_offset_seconds"])
    for match_id, values in orders.items():
        if values != sorted(values):
            errors.append(f"replay_order not monotonic for {match_id}")
    for match_id, values in offsets.items():
        if values != sorted(values):
            errors.append(f"replay_offset_seconds not monotonic for {match_id}")
    report = {
        "status": "PASSED" if not errors else "FAILED",
        "event_count": count,
        "unique_synthetic_event_ids": len(seen_ids),
        "blocking_errors": errors,
        "partition_key": "synthetic_match_id",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if errors:
        raise SystemExit(json.dumps(report, indent=2))
    print(f"Replay dry-run validation PASSED: events={count}")


if __name__ == "__main__":
    main()
