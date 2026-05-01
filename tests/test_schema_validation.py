import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_contracts_and_curated_parquet_schema_exist():
    contract = ROOT / "contracts" / "curated_point_schema.json"
    assert contract.exists()
    schema = json.loads(contract.read_text())
    required = schema["required"]
    parts = sorted((ROOT / "data" / "curated" / "singles_points").glob("part-*.parquet"))
    assert parts
    df = pd.read_parquet(parts[0])
    assert list(df.columns) == required


def test_required_zone_metadata_exists():
    assert (ROOT / "data" / "cleaned" / "zone_metadata.json").exists()
    assert (ROOT / "data" / "curated" / "zone_metadata.json").exists()
