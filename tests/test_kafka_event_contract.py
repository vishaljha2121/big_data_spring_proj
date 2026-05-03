import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]


def test_dry_run_events_match_point_event_schema():
    schema = json.loads((ROOT / "contracts/point_event_schema.json").read_text(encoding="utf-8"))
    lines = (ROOT / "data/results/replay_dry_run/sample_events.jsonl").read_text(encoding="utf-8").splitlines()[:25]
    assert lines
    for line in lines:
        event = json.loads(line)
        jsonschema.validate(event, schema)
        assert set(event) == set(schema["required"])
