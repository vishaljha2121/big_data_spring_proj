from pathlib import Path
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_player_baselines import quality_level


def test_baseline_quality_thresholds():
    assert quality_level(200, False) == "strong"
    assert quality_level(50, False) == "moderate"
    assert quality_level(49, False) == "weak"
    assert quality_level(500, True) == "invalid_or_placeholder"


def test_unknown_placeholders_are_not_strong_baselines():
    parts = sorted((ROOT / "data" / "baselines" / "player_baselines").glob("part-*.parquet"))
    assert parts
    baselines = pd.concat([pd.read_parquet(path) for path in parts], ignore_index=True)
    placeholders = baselines[baselines["is_unknown_placeholder"]]
    assert not ((placeholders["baseline_quality_level"] == "strong").any())


def test_serve_return_counts_are_non_negative_and_bounded():
    parts = sorted((ROOT / "data" / "baselines" / "player_baselines").glob("part-*.parquet"))
    baselines = pd.concat([pd.read_parquet(path) for path in parts], ignore_index=True)
    for col in ["serve_points", "serve_points_won", "return_points", "return_points_won", "aces", "double_faults"]:
        assert (baselines[col] >= 0).all()
    assert (baselines["serve_points_won"] <= baselines["serve_points"]).all()
    assert (baselines["return_points_won"] <= baselines["return_points"]).all()
    assert (baselines["aces"] <= baselines["serve_points"]).all()
    assert (baselines["double_faults"] <= baselines["serve_points"]).all()
