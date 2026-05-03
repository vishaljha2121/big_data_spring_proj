import json
from pathlib import Path
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from model_artifact_lib import score_risk_row  # noqa: E402


def test_risk_config_scores_fixture_without_fake_labels():
    model_dir = ROOT / "data/models/risk/v1"
    config = json.loads((model_dir / "risk_config.json").read_text(encoding="utf-8"))
    fixture = pd.read_parquet(model_dir / "validation_fixture.parquet").head(1)
    score = score_risk_row(fixture.iloc[0].to_dict(), config)
    assert config["fake_labels_used"] is False
    assert 0.0 <= score["risk_score"] <= 1.0
    assert score["risk_bucket"] in {"low", "medium", "high"}
