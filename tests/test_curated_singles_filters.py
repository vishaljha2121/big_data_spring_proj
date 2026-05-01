import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_curated_singles_excludes_doubles_and_mixed_sources():
    parts = sorted((ROOT / "data" / "curated" / "singles_points").glob("part-*.parquet"))
    assert parts
    for path in parts:
        df = pd.read_parquet(path, columns=["source_file"])
        source = df["source_file"].astype("string")
        assert not source.str.contains("doubles", case=False, na=False).any()
        assert not source.str.contains("mixed", case=False, na=False).any()


def test_excluded_rows_are_reported():
    report = json.loads((ROOT / "data" / "cleaned" / "data_quality_report.json").read_text())
    assert report["excluded_doubles_files"] > 0
    assert report["excluded_doubles_rows"] > 0
    assert report["excluded_mixed_files"] > 0
    assert report["excluded_mixed_rows"] > 0
