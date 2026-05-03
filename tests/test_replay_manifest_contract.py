from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_replay_manifest_has_canonical_columns():
    df = pd.read_parquet(ROOT / "data/replay/manifests/replay_manifest_v1.parquet", columns=[
        "replay_session_id",
        "synthetic_match_id",
        "synthetic_event_id",
        "replay_order",
        "replay_offset_seconds",
    ])
    assert len(df) > 0
    assert df["synthetic_event_id"].is_unique
    assert df["synthetic_match_id"].notna().all()
