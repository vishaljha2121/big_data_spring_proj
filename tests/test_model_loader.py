from pathlib import Path

import pandas as pd

from streaming.model_loader import OddsModelLoader, RiskConfigLoader


ROOT = Path(__file__).resolve().parents[1]


def test_model_loader_loads_published_odds_and_risk_artifacts():
    odds = OddsModelLoader(ROOT / "data/models/odds/latest.json")
    risk = RiskConfigLoader(ROOT / "data/models/risk/latest.json")
    assert odds.feature_columns
    assert odds.feature_schema_hash
    assert odds.target_column == "label_point_winner_is_player_a"
    assert risk.version == "v1"
    assert risk.config["fake_labels_used"] is False


def test_model_loader_scores_numeric_fixture_probabilities():
    odds = OddsModelLoader(ROOT / "data/models/odds/latest.json")
    frame = pd.DataFrame([{column: 0.0 for column in odds.feature_columns}])
    probabilities = odds.predict_proba(frame)
    assert len(probabilities) == 1
    assert 0.0 <= probabilities[0] <= 1.0
