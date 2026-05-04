import json
from pathlib import Path

from streaming.stream_scorer import StreamScorer


ROOT = Path(__file__).resolve().parents[1]


def test_stream_scorer_scores_replay_jsonl_events():
    scorer = StreamScorer(ROOT / "data/models/odds/latest.json", ROOT / "data/models/risk/latest.json")
    events = []
    with (ROOT / "data/results/replay_dry_run/sample_events.jsonl").open("r", encoding="utf-8") as handle:
        for _, line in zip(range(3), handle):
            events.append(json.loads(line))
    scored = [scorer.score_event(event) for event in events]
    assert len(scored) == 3
    for event in scored:
        assert 0.0 <= event["point_probability_player_a"] <= 1.0
        assert 0.0 <= event["point_probability_player_b"] <= 1.0
        assert abs(event["point_probability_player_a"] + event["point_probability_player_b"] - 1.0) < 1e-6
        assert event["odds_model_version"] == "v1"
