#!/usr/bin/env python3
"""Validate published outcome models against their validation fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

def validate_target(target_name: str) -> None:
    publish_dir = ROOT / f"data/models/outcomes/{target_name}/v1"
    if not publish_dir.exists():
        return
        
    model = joblib.load(publish_dir / "model.joblib")
    schema = json.loads((publish_dir / "feature_schema.json").read_text(encoding="utf-8"))
    expected_preds = json.loads((publish_dir / "validation_predictions.json").read_text(encoding="utf-8"))["predictions"]
    
    df = pd.read_parquet(publish_dir / "validation_fixture.parquet")
    preds = model.predict_proba(df[schema["feature_columns"]])[:, 1].tolist()
    
    # Check max difference
    diff = max(abs(a - b) for a, b in zip(preds, expected_preds))
    if diff > 1e-4:
        raise ValueError(f"[{target_name.upper()}] Predictions do not match fixture! Max diff: {diff}")
        
    print(f"[{target_name.upper()}] Validation passed (max diff: {diff:.6e})")

def main() -> None:
    for t in ["game", "set", "match"]:
        validate_target(t)

if __name__ == "__main__":
    main()
