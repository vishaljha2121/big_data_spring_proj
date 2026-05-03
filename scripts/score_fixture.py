#!/usr/bin/env python3
"""Score published odds or risk validation fixtures."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd

from model_artifact_lib import read_json, score_odds_dataframe, score_risk_row, write_json


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", type=Path, default=Path("data/models"))
    parser.add_argument("--model-type", choices=["odds", "risk"], required=True)
    parser.add_argument("--version", default="v1")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    model_dir = args.models / args.model_type / args.version
    if args.model_type == "odds":
        model = joblib.load(model_dir / "model.joblib")
        schema = read_json(model_dir / "feature_schema.json")
        fixture = pd.read_parquet(model_dir / "validation_fixture.parquet")
        predictions = score_odds_dataframe(model, fixture, schema["feature_columns"])
        payload = {"predictions": predictions}
    else:
        config = read_json(model_dir / "risk_config.json")
        fixture = pd.read_parquet(model_dir / "validation_fixture.parquet")
        payload = {"scores": [score_risk_row(row, config) for row in fixture.to_dict(orient="records")]}
    out = args.out or (model_dir / ("validation_predictions.json" if args.model_type == "odds" else "validation_scores.json"))
    write_json(out, payload)
    print(f"Scored fixture: {out}")


if __name__ == "__main__":
    main()
