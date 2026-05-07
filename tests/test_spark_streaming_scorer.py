import json
from pathlib import Path

import jsonschema

from spark_streaming.kafka_streaming_scorer import score_event_batch
from streaming.stream_scorer import StreamScorer


ROOT = Path(__file__).resolve().parents[1]


def sample_event(index=0):
    return {
        "schema_version": "point_event_v1",
        "replay_session_id": "test-session",
        "synthetic_match_id": "synthetic-test-match",
        "source_match_id": "source-test-match",
        "event_id": f"event-{index}",
        "synthetic_event_id": f"synthetic-event-{index}",
        "event_index": index,
        "replay_order": index,
        "replay_offset_seconds": float(index * 2),
        "event_ts": "2026-01-01T00:00:00Z",
        "player_a": "Player A",
        "player_b": "Player B",
        "server_player": "Player A" if index % 2 == 0 else "Player B",
        "receiver_player": "Player B" if index % 2 == 0 else "Player A",
        "point_winner_player": "Player A" if index % 2 == 0 else "Player B",
        "set_number": 1,
        "game_number": 1,
        "point_number": index + 1,
        "p1_score": "0",
        "p2_score": "0",
        "is_ace": False,
        "is_double_fault": False,
        "is_break_point": False,
        "source_file": "synthetic",
    }


def test_foreach_batch_scoring_helper_scores_schema_valid_rows(tmp_path):
    scorer = StreamScorer(ROOT / "data/models/odds/latest.json", ROOT / "data/models/risk/latest.json")
    events = [sample_event(i) for i in range(5)]
    report = score_event_batch(events, scorer, tmp_path / "out.jsonl", tmp_path / "parquet", batch_id=3)
    assert report["scored_count"] == 5
    rows = [json.loads(line) for line in (tmp_path / "out.jsonl").read_text(encoding="utf-8").splitlines()]
    schema = json.loads((ROOT / "contracts/scored_event_schema.json").read_text(encoding="utf-8"))
    for row in rows:
        jsonschema.validate(row, schema)
        assert 0 <= row["point_probability_player_a"] <= 1
        assert 0 <= row["risk_score"] <= 1
