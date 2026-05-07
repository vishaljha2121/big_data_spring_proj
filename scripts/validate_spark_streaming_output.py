#!/usr/bin/env python3
"""Validate Spark Structured Streaming scored output."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import jsonschema
import pandas as pd


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_jsonl_dir(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if path.is_file():
        files = [path]
    else:
        files = sorted(path.glob("*.jsonl"))
    for file_path in files:
        with file_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    rows.append(json.loads(line))
    return rows


def write_report(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("data/results/spark_streaming"))
    parser.add_argument("--schema", type=Path, default=Path("contracts/scored_event_schema.json"))
    parser.add_argument("--expected-count", type=int, default=1000)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--checkpoint-dir", type=Path, default=Path("data/checkpoints/spark_streaming_scorer"))
    args = parser.parse_args()

    report_path = args.report or args.output_dir / "spark_streaming_validation_report.json"
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    validator = jsonschema.Draft7Validator(schema)
    run_report_path = args.output_dir / "spark_streaming_run_report.json"
    checkpoint = args.checkpoint_dir
    jsonl_dir = args.output_dir / "scored_events_jsonl"
    parquet_dir = args.output_dir / "scored_events_parquet"
    errors: List[str] = []
    warnings: List[str] = []

    if not run_report_path.exists():
        errors.append("missing spark_streaming_run_report.json")
        run_report = None
    else:
        run_report = json.loads(run_report_path.read_text(encoding="utf-8"))
        if run_report.get("status") != "PASSED":
            errors.append(f"run report status is {run_report.get('status')}")

    if not checkpoint.exists():
        errors.append("checkpoint directory missing")
    rows = read_jsonl_dir(jsonl_dir) if jsonl_dir.exists() else []
    if len(rows) < args.expected_count:
        errors.append(f"expected at least {args.expected_count} scored events, found {len(rows)}")

    schema_errors = []
    prob_errors = 0
    risk_errors = 0
    invalid_flags = 0
    synthetic_ids = set()
    duplicate_ids = 0
    for index, row in enumerate(rows):
        validation_errors = list(validator.iter_errors(row))
        if validation_errors:
            schema_errors.append({"index": index, "error": validation_errors[0].message})
        pa = row.get("point_probability_player_a")
        pb = row.get("point_probability_player_b")
        if not isinstance(pa, (int, float)) or not isinstance(pb, (int, float)) or not (0 <= pa <= 1) or not (0 <= pb <= 1):
            prob_errors += 1
        risk = row.get("risk_score")
        if not isinstance(risk, (int, float)) or not (0 <= risk <= 1) or row.get("risk_bucket") not in {"low", "medium", "high"}:
            risk_errors += 1
        if row.get("input_event_valid") is not True or row.get("feature_row_valid") is not True:
            invalid_flags += 1
        sid = row.get("synthetic_event_id")
        if sid in synthetic_ids:
            duplicate_ids += 1
        if sid:
            synthetic_ids.add(sid)
    if schema_errors:
        errors.append(f"{len(schema_errors)} scored events failed schema validation")
    if prob_errors:
        errors.append(f"{prob_errors} scored events had invalid probabilities")
    if risk_errors:
        errors.append(f"{risk_errors} scored events had invalid risk outputs")
    if invalid_flags:
        errors.append(f"{invalid_flags} scored events had invalid flags")
    if duplicate_ids:
        errors.append(f"{duplicate_ids} duplicate synthetic_event_id values found")

    parquet_files = sorted(parquet_dir.glob("*.parquet")) if parquet_dir.exists() else []
    parquet_rows = 0
    for parquet_file in parquet_files:
        parquet_rows += len(pd.read_parquet(parquet_file))
    if not parquet_files:
        warnings.append("no parquet batch files found")

    report = {
        "generated_at": now_iso(),
        "status": "PASSED" if not errors else "FAILED",
        "expected_count": args.expected_count,
        "jsonl_event_count": len(rows),
        "parquet_file_count": len(parquet_files),
        "parquet_event_count": parquet_rows,
        "checkpoint_exists": checkpoint.exists(),
        "run_report_exists": run_report_path.exists(),
        "schema_error_examples": schema_errors[:5],
        "warnings": warnings,
        "blocking_errors": errors,
    }
    write_report(report_path, report)
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
