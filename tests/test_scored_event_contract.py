import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]


def test_scored_event_sample_matches_contract():
    schema = json.loads((ROOT / "contracts/scored_event_schema.json").read_text(encoding="utf-8"))
    with (ROOT / "data/results/streaming_scoring/scored_events_sample.jsonl").open("r", encoding="utf-8") as handle:
        event = json.loads(next(handle))
    jsonschema.validate(event, schema)
    assert "match_win_probability" not in event
    assert "point_probability_player_a" in event
