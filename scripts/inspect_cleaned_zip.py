#!/usr/bin/env python3
"""Inventory the teammate-provided cleaned CSV staging inputs."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import zipfile
from pathlib import Path

from data_layer_lib import inspect_inputs, write_json


def inspect_zip(path: Path) -> dict:
    entries = []
    with zipfile.ZipFile(path) as archive:
        for name in sorted(archive.namelist()):
            if not name.endswith(".csv.gz"):
                continue
            with archive.open(name) as raw:
                with gzip.open(raw, "rt", newline="") as handle:
                    reader = csv.reader(handle)
                    header = next(reader)
                    rows = sum(1 for _ in reader)
            classification = "point" if "points_cleaned_parts/" in name else "metadata" if name.endswith("match_metadata_cleaned.csv.gz") else "atp_matches" if name.endswith("atp_matches_cleaned.csv.gz") else "other"
            if "-doubles_" in name:
                classification = "doubles"
            elif "-mixed_" in name:
                classification = "mixed"
            elif "points_cleaned_parts/" in name:
                classification = "singles"
            entries.append({"path": name, "rows": rows, "columns": header, "classification": classification})
    point_entries = [e for e in entries if e["classification"] in {"singles", "doubles", "mixed"}]
    return {
        "input_path": str(path),
        "total_files_seen": len(entries),
        "point_files_seen": len(point_entries),
        "metadata_files_seen": len([e for e in entries if e["classification"] == "metadata"]),
        "atp_match_files_seen": len([e for e in entries if e["classification"] == "atp_matches"]),
        "singles_point_files_seen": len([e for e in entries if e["classification"] == "singles"]),
        "doubles_point_files_seen": len([e for e in entries if e["classification"] == "doubles"]),
        "mixed_point_files_seen": len([e for e in entries if e["classification"] == "mixed"]),
        "raw_point_rows": sum(e["rows"] for e in point_entries),
        "singles_point_rows_by_filename": sum(e["rows"] for e in entries if e["classification"] == "singles"),
        "excluded_doubles_rows": sum(e["rows"] for e in entries if e["classification"] == "doubles"),
        "excluded_mixed_rows": sum(e["rows"] for e in entries if e["classification"] == "mixed"),
        "files": entries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("cleaned_data"))
    parser.add_argument("--out", type=Path, default=Path("data/cleaned"))
    args = parser.parse_args()
    payload = inspect_zip(args.input) if args.input.is_file() and args.input.suffix == ".zip" else inspect_inputs(args.input)
    write_json(args.out / "input_inventory.json", payload)
    print(json.dumps({k: payload[k] for k in payload if k != "files" and k != "schema_variants"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
