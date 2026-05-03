#!/usr/bin/env python3
"""Validate the canonical replay manifest contract and ordering."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from producer.replay_producer import REQUIRED_MANIFEST_COLUMNS


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("data/replay/manifests/replay_manifest_v1.parquet"))
    args = parser.parse_args()
    df = pd.read_parquet(args.manifest)
    errors = []
    missing = [column for column in REQUIRED_MANIFEST_COLUMNS if column not in df.columns]
    if missing:
        errors.append(f"missing columns: {missing}")
    if df["synthetic_event_id"].duplicated().any():
        errors.append("synthetic_event_id is not unique")
    for match_id, group in df.sort_values(["synthetic_match_id", "replay_order"]).groupby("synthetic_match_id"):
        if group["replay_order"].tolist() != sorted(group["replay_order"].tolist()):
            errors.append(f"replay_order not monotonic for {match_id}")
            break
        if group["replay_offset_seconds"].tolist() != sorted(group["replay_offset_seconds"].tolist()):
            errors.append(f"replay_offset_seconds not monotonic for {match_id}")
            break
    report = {"status": "PASSED" if not errors else "FAILED", "rows": int(len(df)), "blocking_errors": errors}
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
