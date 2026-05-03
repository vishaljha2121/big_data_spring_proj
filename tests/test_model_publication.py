import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_odds_latest_points_to_v1_artifact():
    latest = json.loads((ROOT / "data/models/odds/latest.json").read_text(encoding="utf-8"))
    assert latest["status"] == "published"
    assert latest["validation_status"] == "passed"
    assert (ROOT / latest["artifact_path"]).exists()
    assert (ROOT / latest["metadata_path"]).exists()


def test_risk_latest_points_to_v1_artifact():
    latest = json.loads((ROOT / "data/models/risk/latest.json").read_text(encoding="utf-8"))
    assert latest["status"] == "published"
    assert latest["validation_status"] == "passed"
    assert (ROOT / latest["artifact_path"]).exists()
    assert (ROOT / latest["metadata_path"]).exists()
