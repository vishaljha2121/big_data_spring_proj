import json
from pathlib import Path

import joblib
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_odds_artifact_loads_with_feature_schema():
    model_dir = ROOT / "data/models/odds/v1"
    model = joblib.load(model_dir / "model.joblib")
    schema = json.loads((model_dir / "feature_schema.json").read_text(encoding="utf-8"))
    fixture = pd.read_parquet(model_dir / "validation_fixture.parquet").head(10)
    assert schema["feature_columns"]
    probabilities = model.predict_proba(fixture[schema["feature_columns"]])[:, 1]
    assert all(0.0 <= float(value) <= 1.0 for value in probabilities)
