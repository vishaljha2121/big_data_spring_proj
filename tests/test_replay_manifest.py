from pathlib import Path
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_replay_manifests import stable_id


def _manifest():
    path = ROOT / "data" / "replay" / "manifests" / "replay_manifest_v1.parquet"
    assert path.exists()
    return pd.read_parquet(path)


def test_deterministic_ids():
    manifest = _manifest()
    expected_match_ids = manifest["source_match_id"].map(lambda x: stable_id("synthetic_match", x, 42))
    assert manifest["synthetic_match_id"].astype(str).equals(expected_match_ids.astype(str))
    expected_event_ids = [
        stable_id("synthetic_event", row.synthetic_match_id, row.event_id, row.event_index, 42, length=24)
        for row in manifest[["synthetic_match_id", "event_id", "event_index"]].itertuples(index=False)
    ]
    assert manifest["synthetic_event_id"].tolist() == expected_event_ids


def test_synthetic_event_id_uniqueness():
    manifest = _manifest()
    assert manifest["synthetic_event_id"].is_unique


def test_replay_order_monotonic():
    manifest = _manifest()
    assert manifest.groupby("synthetic_match_id")["replay_order"].apply(lambda s: s.is_monotonic_increasing).all()


def test_replay_offset_seconds_monotonic():
    manifest = _manifest()
    assert manifest.groupby("synthetic_match_id")["replay_offset_seconds"].apply(lambda s: s.is_monotonic_increasing).all()
