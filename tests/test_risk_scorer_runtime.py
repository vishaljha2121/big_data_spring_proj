import json
from pathlib import Path

from streaming.risk_scorer import RuntimeRiskScorer


ROOT = Path(__file__).resolve().parents[1]


def test_runtime_risk_scorer_outputs_valid_bucket_without_fake_labels():
    latest = json.loads((ROOT / "data/models/risk/latest.json").read_text(encoding="utf-8"))
    config = json.loads((ROOT / latest["artifact_path"]).read_text(encoding="utf-8"))
    scorer = RuntimeRiskScorer(config)
    output = scorer.score(
        {
            "server_point_win_pct_before": 0.55,
            "receiver_point_win_pct_before": 0.45,
        }
    )
    assert 0.0 <= output["risk_score"] <= 1.0
    assert output["risk_bucket"] in {"low", "medium", "high"}
    assert output["fake_labels_used"] is False
