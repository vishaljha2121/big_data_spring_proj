import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from producer.replay_producer import load_manifest, load_schema, manifest_row_to_event, validate_event  # noqa: E402


def test_manifest_row_serializes_to_canonical_event():
    df = load_manifest(ROOT / "data/replay/manifests/replay_manifest_v1.parquet", max_events=1, max_matches=None, seed=42)
    event = manifest_row_to_event(df.iloc[0].to_dict())
    validate_event(event, load_schema(ROOT / "contracts/point_event_schema.json"))
    assert event["schema_version"] == "point_event_v1"
    assert "player_a_point_win_pct_before" not in event


def test_dry_run_output_exists_and_is_jsonl():
    path = ROOT / "data/results/replay_dry_run/sample_events.jsonl"
    first = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
    assert first["schema_version"] == "point_event_v1"
    assert first["synthetic_match_id"]
