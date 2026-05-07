#!/usr/bin/env python3
"""Validate the local observability snapshot against its schema."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    schema_path = ROOT / "contracts/observability_snapshot_schema.json"
    snapshot_path = ROOT / "data/results/observability/observability_snapshot.json"
    report_path = ROOT / "data/results/observability/observability_validation_report.json"
    
    if not schema_path.exists() or not snapshot_path.exists():
        print("Schema or snapshot missing. Run generate_observability_snapshot.py first.")
        return
        
    schema = json.loads(schema_path.read_text())
    snapshot = json.loads(snapshot_path.read_text())
    
    try:
        jsonschema.validate(snapshot, schema)
        report = {
            "status": "PASSED",
            "message": "Observability snapshot conforms to schema."
        }
        print("Observability validation PASSED.")
    except jsonschema.ValidationError as exc:
        report = {
            "status": "FAILED",
            "message": str(exc)
        }
        print(f"Observability validation FAILED: {exc}")
        
    report_path.write_text(json.dumps(report, indent=2) + "\n")

if __name__ == "__main__":
    main()
