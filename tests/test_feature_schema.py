import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_point_and_match_feature_schemas_match_outputs():
    point_schema = json.loads((ROOT / "contracts" / "point_feature_schema.json").read_text())
    match_schema = json.loads((ROOT / "contracts" / "match_feature_schema.json").read_text())
    point_parts = sorted((ROOT / "data" / "features" / "point_features").glob("part-*.parquet"))
    match_parts = sorted((ROOT / "data" / "features" / "match_features").glob("part-*.parquet"))
    assert point_parts
    assert match_parts
    point_df = pd.read_parquet(point_parts[0])
    match_df = pd.read_parquet(match_parts[0])
    assert set(point_schema["required"]).issubset(point_df.columns)
    assert set(match_schema["required"]).issubset(match_df.columns)


def test_required_milestone_2a_files_exist():
    required = [
        ROOT / "data" / "features" / "feature_build_report.json",
        ROOT / "data" / "features" / "feature_quality_report.json",
        ROOT / "data" / "baselines" / "baseline_quality_report.json",
        ROOT / "data" / "replay" / "replay_manifest_report.json",
        ROOT / "data" / "replay" / "manifests" / "replay_manifest_v1.parquet",
        ROOT / "data" / "replay" / "manifests" / "replay_manifest_v1.json",
        ROOT / "docs" / "feature_engineering_audit.md",
        ROOT / "docs" / "baseline_generation_audit.md",
        ROOT / "docs" / "replay_manifest_audit.md",
        ROOT / "docs" / "next_implementation_steps.md",
    ]
    for path in required:
        assert path.exists(), path
