#!/usr/bin/env python3
"""Validate scored event JSONL output and scoring run reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import jsonschema


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--odds-latest", type=Path, required=True)
    parser.add_argument("--run-report", type=Path, default=Path("data/results/streaming_scoring/scoring_run_report.json"))
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--expected-count", type=int, default=None)
    args = parser.parse_args()

    errors: List[str] = []
    schema = read_json(args.schema)
    odds_latest = read_json(args.odds_latest)
    run_report = read_json(args.run_report)
    if run_report.get("status") != "PASSED":
        errors.append("scoring_run_report status is not PASSED")
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
                errors.append(f"line {line_no}: schema validation failed: {exc}")
                continue
            pa = event["point_probability_player_a"]
            pb = event["point_probability_player_b"]
            if not (0.0 <= pa <= 1.0 and 0.0 <= pb <= 1.0):
                errors.append(f"line {line_no}: probability outside [0,1]")
            if abs((pa + pb) - 1.0) > 1e-6:
                errors.append(f"line {line_no}: probabilities do not sum to 1")
            if not (0.0 <= event["risk_score"] <= 1.0):
                errors.append(f"line {line_no}: risk_score outside [0,1]")
            if event["risk_bucket"] not in {"low", "medium", "high"}:
                errors.append(f"line {line_no}: invalid risk bucket")
            if event["feature_schema_hash"] != odds_latest["feature_schema_hash"]:
                errors.append(f"line {line_no}: feature schema hash mismatch")
            if event["input_event_valid"] is not True or event["feature_row_valid"] is not True:
                errors.append(f"line {line_no}: invalid input/feature flags")
    if not args.events.exists():
        errors.append("scored events output does not exist")
    if args.expected_count is not None and count < args.expected_count:
        errors.append(f"expected at least {args.expected_count} events, found {count}")
    report = {
        "status": "PASSED" if not errors else "FAILED",
        "event_count": count,
        "blocking_errors": errors,
    }
    write_json(args.report, report)
    if errors:
        raise SystemExit(json.dumps(report, indent=2))
    print(f"Scored event validation PASSED: events={count}")


if __name__ == "__main__":
    main()
