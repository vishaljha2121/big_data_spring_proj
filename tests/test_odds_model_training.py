import json
from pathlib import Path

import joblib
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_published_odds_model_scores_fixture():
    model_dir = ROOT / "data/models/odds/v1"
    model = joblib.load(model_dir / "model.joblib")
    schema = json.loads((model_dir / "feature_schema.json").read_text(encoding="utf-8"))
    fixture = pd.read_parquet(model_dir / "validation_fixture.parquet").head(25)
    probabilities = model.predict_proba(fixture[schema["feature_columns"]])[:, 1]
    assert len(probabilities) == len(fixture)
    assert ((probabilities >= 0.0) & (probabilities <= 1.0)).all()


def test_odds_metadata_has_required_fields_and_gates():
    metadata = json.loads((ROOT / "data/models/odds/v1/metadata.json").read_text(encoding="utf-8"))
    assert metadata["model_type"] == "odds"
    assert metadata["target_column"] == "label_point_winner_is_player_a"
    assert metadata["validation_auc"] >= 0.55
    assert metadata["test_auc"] >= 0.55
    assert metadata["validation_brier_score"] <= 0.30
    assert metadata["test_brier_score"] <= 0.30
    assert "match_id" not in metadata["feature_columns"]
    assert "event_id" not in metadata["feature_columns"]
