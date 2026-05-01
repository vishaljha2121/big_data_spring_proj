#!/usr/bin/env python3
"""Utilities for the Milestone 1B tennis data layer."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import pandas as pd

SCHEMA_VERSION = "1.0.0"

POINT_COLUMNS = [
    "match_id",
    "ElapsedTime",
    "SetNo",
    "P1GamesWon",
    "P2GamesWon",
    "SetWinner",
    "GameNo",
    "GameWinner",
    "PointNumber",
    "PointWinner",
    "PointServer",
    "Speed_KMH",
    "Speed_MPH",
    "Rally",
    "P1Score",
    "P2Score",
    "P1PointsWon",
    "P2PointsWon",
    "P1Ace",
    "P2Ace",
    "P1Winner",
    "P2Winner",
    "P1DoubleFault",
    "P2DoubleFault",
    "P1UnfErr",
    "P2UnfErr",
    "P1BreakPoint",
    "P2BreakPoint",
    "P1BreakPointWon",
    "P2BreakPointWon",
    "P1FirstSrvIn",
    "P2FirstSrvIn",
    "P1FirstSrvWon",
    "P2FirstSrvWon",
    "P1SecondSrvIn",
    "P2SecondSrvIn",
    "P1SecondSrvWon",
    "P2SecondSrvWon",
    "P1ForcedError",
    "P2ForcedError",
    "ServeIndicator",
    "source_file",
    "event_id",
]

CURATED_POINT_COLUMNS = [
    "event_id",
    "match_id",
    "source_match_id",
    "event_index",
    "year",
    "slam",
    "tournament",
    "surface",
    "player_a",
    "player_b",
    "server_player",
    "receiver_player",
    "point_winner_player",
    "set_number",
    "game_number",
    "point_number",
    "p1_score",
    "p2_score",
    "p1_games_won",
    "p2_games_won",
    "rally_length",
    "serve_speed_kmh",
    "serve_speed_mph",
    "is_ace",
    "is_double_fault",
    "is_break_point",
    "elapsed_seconds",
    "source_file",
    "schema_version",
    "replay_session_id",
    "synthetic_match_id",
    "event_ts",
]

CURATED_DTYPE = {
    "event_id": "string",
    "match_id": "string",
    "source_match_id": "string",
    "event_index": "Int64",
    "year": "Int64",
    "slam": "string",
    "tournament": "string",
    "surface": "string",
    "player_a": "string",
    "player_b": "string",
    "server_player": "string",
    "receiver_player": "string",
    "point_winner_player": "string",
    "set_number": "Int64",
    "game_number": "Int64",
    "point_number": "Int64",
    "p1_score": "string",
    "p2_score": "string",
    "p1_games_won": "Int64",
    "p2_games_won": "Int64",
    "rally_length": "Int64",
    "serve_speed_kmh": "float64",
    "serve_speed_mph": "float64",
    "is_ace": "boolean",
    "is_double_fault": "boolean",
    "is_break_point": "boolean",
    "elapsed_seconds": "float64",
    "source_file": "string",
    "schema_version": "string",
    "replay_session_id": "string",
    "synthetic_match_id": "string",
}

REPORT_KEYS = [
    "generated_at",
    "input_archive",
    "schema_version",
    "total_files_seen",
    "point_files_seen",
    "metadata_files_seen",
    "atp_match_files_seen",
    "raw_point_rows",
    "raw_metadata_rows",
    "raw_atp_match_rows",
    "curated_singles_point_rows",
    "curated_singles_match_count",
    "excluded_doubles_files",
    "excluded_doubles_rows",
    "excluded_mixed_files",
    "excluded_mixed_rows",
    "duplicate_event_id_count",
    "missing_match_id_count",
    "missing_event_id_count",
    "metadata_join_success_count",
    "metadata_join_missing_count",
    "invalid_point_winner_count",
    "invalid_point_server_count",
    "special_point_number_count",
    "missing_elapsed_time_count",
    "missing_rally_length_count",
    "missing_surface_count",
    "quarantined_row_count",
    "warnings",
    "blocking_errors",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_text(value: Any) -> Optional[str]:
    if value is None or pd.isna(value):
        return None
    s = str(value).strip()
    return s if s else None


def to_int_nullable(value: Any) -> Optional[int]:
    s = norm_text(value)
    if s is None:
        return None
    if re.fullmatch(r"[+-]?\d+", s):
        return int(s)
    if re.fullmatch(r"[+-]?\d+\.0+", s):
        return int(float(s))
    return None


def to_float_nullable(value: Any) -> Optional[float]:
    s = norm_text(value)
    if s is None:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def normalize_code(value: Any) -> Optional[int]:
    s = norm_text(value)
    if s is None:
        return None
    if s in {"1", "1.0"}:
        return 1
    if s in {"2", "2.0"}:
        return 2
    return None


def is_invalid_code(value: Any) -> bool:
    s = norm_text(value)
    return s is not None and normalize_code(s) is None


def parse_bool_01(value: Any) -> Optional[bool]:
    s = norm_text(value)
    if s is None:
        return None
    if s in {"1", "1.0", "true", "True", "TRUE"}:
        return True
    if s in {"0", "0.0", "false", "False", "FALSE"}:
        return False
    return None


def parse_elapsed_seconds(value: Any) -> Optional[float]:
    s = norm_text(value)
    if s is None:
        return None
    parts = s.split(":")
    if len(parts) != 3:
        return None
    try:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])
    except ValueError:
        return None
    if hours < 0 or minutes < 0 or seconds < 0 or minutes >= 60 or seconds >= 60:
        return None
    return float(hours * 3600 + minutes * 60 + seconds)


def parse_event_suffix(event_id: Any) -> Optional[int]:
    s = norm_text(event_id)
    if s is None:
        return None
    m = re.search(r"_(\d+)$", s)
    return int(m.group(1)) if m else None


def classify_point_file(path: Path) -> str:
    name = path.name
    if "-doubles_" in name:
        return "doubles"
    if "-mixed_" in name:
        return "mixed"
    return "singles"


def discover_inputs(input_path: Path) -> Dict[str, List[Path]]:
    if input_path.is_file() and input_path.suffix == ".zip":
        raise NotImplementedError("Zip input should be extracted before build steps; inspect supports archive listing only.")
    all_csv = sorted(input_path.rglob("*.csv.gz"))
    points = sorted([p for p in all_csv if "points_cleaned_parts" in p.parts])
    metadata = sorted([p for p in all_csv if p.name == "match_metadata_cleaned.csv.gz"])
    atp = sorted([p for p in all_csv if p.name == "atp_matches_cleaned.csv.gz"])
    singles = [p for p in points if classify_point_file(p) == "singles"]
    doubles = [p for p in points if classify_point_file(p) == "doubles"]
    mixed = [p for p in points if classify_point_file(p) == "mixed"]
    return {
        "all_csv": all_csv,
        "points": points,
        "metadata": metadata,
        "atp": atp,
        "singles": singles,
        "doubles": doubles,
        "mixed": mixed,
    }


def csv_gz_header_and_count(path: Path) -> Tuple[List[str], int]:
    with gzip.open(path, "rt", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        rows = sum(1 for _ in reader)
    return header, rows


def inspect_inputs(input_path: Path) -> Dict[str, Any]:
    files = discover_inputs(input_path)
    file_entries = []
    schema_variants: Dict[str, Dict[str, Any]] = {}
    row_counts: Dict[str, int] = {}
    for path in files["all_csv"]:
        header, rows = csv_gz_header_and_count(path)
        rel = str(path.relative_to(input_path))
        digest = hashlib.sha256(",".join(header).encode("utf-8")).hexdigest()
        row_counts[rel] = rows
        schema_variants.setdefault(digest, {"columns": header, "files": []})["files"].append(rel)
        file_entries.append(
            {
                "path": rel,
                "rows": rows,
                "columns": header,
                "classification": (
                    classify_point_file(path)
                    if "points_cleaned_parts" in path.parts
                    else "metadata"
                    if path.name == "match_metadata_cleaned.csv.gz"
                    else "atp_matches"
                    if path.name == "atp_matches_cleaned.csv.gz"
                    else "other"
                ),
                "sha256": sha256_file(path),
            }
        )
    point_rows = sum(row_counts[str(p.relative_to(input_path))] for p in files["points"])
    doubles_rows = sum(row_counts[str(p.relative_to(input_path))] for p in files["doubles"])
    mixed_rows = sum(row_counts[str(p.relative_to(input_path))] for p in files["mixed"])
    singles_rows = sum(row_counts[str(p.relative_to(input_path))] for p in files["singles"])
    return {
        "generated_at": now_iso(),
        "input_path": str(input_path),
        "total_files_seen": len(files["all_csv"]),
        "point_files_seen": len(files["points"]),
        "metadata_files_seen": len(files["metadata"]),
        "atp_match_files_seen": len(files["atp"]),
        "singles_point_files_seen": len(files["singles"]),
        "doubles_point_files_seen": len(files["doubles"]),
        "mixed_point_files_seen": len(files["mixed"]),
        "raw_point_rows": point_rows,
        "singles_point_rows_by_filename": singles_rows,
        "excluded_doubles_rows": doubles_rows,
        "excluded_mixed_rows": mixed_rows,
        "schema_variants": schema_variants,
        "files": file_entries,
    }


def read_csv_strings(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, compression="gzip", dtype="string", keep_default_na=False)


def write_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False, engine="pyarrow")


def write_contracts(root: Path) -> None:
    contracts = root / "contracts"
    contracts.mkdir(parents=True, exist_ok=True)
    common_string = {"type": ["string", "null"]}
    common_int = {"type": ["integer", "null"]}
    curated_props = {
        "event_id": {"type": "string"},
        "match_id": {"type": "string"},
        "source_match_id": common_string,
        "event_index": {"type": "integer"},
        "year": common_int,
        "slam": common_string,
        "tournament": common_string,
        "surface": common_string,
        "player_a": {"type": "string"},
        "player_b": {"type": "string"},
        "server_player": common_string,
        "receiver_player": common_string,
        "point_winner_player": common_string,
        "set_number": common_int,
        "game_number": common_int,
        "point_number": common_int,
        "p1_score": common_string,
        "p2_score": common_string,
        "p1_games_won": common_int,
        "p2_games_won": common_int,
        "rally_length": common_int,
        "serve_speed_kmh": {"type": ["number", "null"]},
        "serve_speed_mph": {"type": ["number", "null"]},
        "is_ace": {"type": "boolean"},
        "is_double_fault": {"type": "boolean"},
        "is_break_point": {"type": ["boolean", "null"]},
        "elapsed_seconds": {"type": ["number", "null"]},
        "source_file": {"type": "string"},
        "schema_version": {"type": "string"},
        "replay_session_id": common_string,
        "synthetic_match_id": common_string,
        "event_ts": common_string,
    }
    curated_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CuratedSinglesPoint",
        "type": "object",
        "required": CURATED_POINT_COLUMNS,
        "additionalProperties": False,
        "properties": curated_props,
    }
    point_event_schema = dict(curated_schema)
    point_event_schema["title"] = "PointEvent"
    metadata_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "MatchMetadata",
        "type": "object",
        "required": ["match_id", "year", "slam", "player1", "player2", "source_file"],
        "properties": {
            "match_id": {"type": "string"},
            "year": common_int,
            "slam": common_string,
            "player1": {"type": "string"},
            "player2": {"type": "string"},
            "source_file": {"type": "string"},
        },
        "additionalProperties": True,
    }
    report_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "DataQualityReport",
        "type": "object",
        "required": REPORT_KEYS,
        "additionalProperties": True,
        "properties": {
            key: {"type": "array"} if key in {"warnings", "blocking_errors"} else {}
            for key in REPORT_KEYS
        },
    }
    write_json(contracts / "curated_point_schema.json", curated_schema)
    write_json(contracts / "point_event_schema.json", point_event_schema)
    write_json(contracts / "match_metadata_schema.json", metadata_schema)
    write_json(contracts / "data_quality_report_schema.json", report_schema)


def build_cleaned_layer(input_path: Path, out_path: Path, root: Path) -> None:
    files = discover_inputs(input_path)
    write_contracts(root)
    staging_readme = root / "data" / "staging" / "cleaned_csv" / "README.md"
    staging_readme.parent.mkdir(parents=True, exist_ok=True)
    staging_readme.write_text(
        "# Staging Cleaned CSV\n\n"
        "The teammate-provided `cleaned_data/` CSV.GZ files are treated as staging input only. "
        "They are preserved in place and converted into validated Parquet outputs under `data/cleaned/` and `data/curated/`.\n",
        encoding="utf-8",
    )
    clean_dir(out_path / "points")
    clean_dir(out_path / "matches")
    clean_dir(out_path / "match_metadata")
    if files["metadata"]:
        metadata = read_csv_strings(files["metadata"][0])
        metadata["year"] = metadata["year"].map(to_int_nullable).astype("Int64")
        write_parquet(metadata.sort_values("match_id").reset_index(drop=True), out_path / "match_metadata" / "part-00000.parquet")
    if files["atp"]:
        atp = read_csv_strings(files["atp"][0])
        write_parquet(atp.sort_values(["tourney_id", "match_num", "atp_match_id"]).reset_index(drop=True), out_path / "matches" / "part-00000.parquet")
    # Cleaned points are standardized staging-level point records, including doubles/mixed.
    for i, path in enumerate(files["points"]):
        df = read_csv_strings(path)
        df = df.reindex(columns=POINT_COLUMNS)
        df["input_classification"] = classify_point_file(path)
        df["input_file"] = str(path.relative_to(input_path))
        write_parquet(df, out_path / "points" / f"part-{i:05d}.parquet")
    zone = {
        "zone": "cleaned",
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_iso(),
        "format": "parquet",
        "source": str(input_path),
        "datasets": {
            "points": len(files["points"]),
            "matches": len(files["atp"]),
            "match_metadata": len(files["metadata"]),
        },
    }
    write_json(out_path / "zone_metadata.json", zone)


def map_player(code: Optional[int], p1: Any, p2: Any) -> Optional[str]:
    if code == 1:
        return norm_text(p1)
    if code == 2:
        return norm_text(p2)
    return None


def participant_name(value: Any, match_id: Any, slot: int) -> str:
    name = norm_text(value)
    if name:
        return name
    mid = norm_text(match_id) or "missing_match_id"
    return f"unknown_player_{slot}:{mid}"


def receiver_for_server(code: Optional[int], p1: Any, p2: Any) -> Optional[str]:
    if code == 1:
        return norm_text(p2)
    if code == 2:
        return norm_text(p1)
    return None


def row_has_invalid_point_number(value: Any) -> bool:
    s = norm_text(value)
    return s is not None and to_int_nullable(s) is None


def add_bool_pair(df: pd.DataFrame, p1_col: str, p2_col: str) -> pd.Series:
    p1 = df[p1_col].map(parse_bool_01)
    p2 = df[p2_col].map(parse_bool_01)
    return (p1.fillna(False) | p2.fillna(False)).astype("boolean")


def coerce_curated_types(df: pd.DataFrame) -> pd.DataFrame:
    for col in CURATED_POINT_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
    df = df[CURATED_POINT_COLUMNS].copy()
    for col, dtype in CURATED_DTYPE.items():
        df[col] = df[col].astype(dtype)
    df["event_ts"] = pd.to_datetime(df["event_ts"], errors="coerce", utc=True)
    return df


def build_curated_singles_layer(input_path: Path, cleaned_path: Path, out_path: Path, quarantine_path: Path) -> Dict[str, Any]:
    files = discover_inputs(input_path)
    clean_dir(out_path / "singles_points")
    clean_dir(out_path / "singles_matches")
    clean_dir(out_path / "replay_candidates")
    clean_dir(quarantine_path / "invalid_points")
    clean_dir(quarantine_path / "invalid_metadata")
    (quarantine_path / "README.md").write_text(
        "# Quarantine\n\nRows with invalid point winner/server codes or special non-integer point numbers are copied here as validation evidence. "
        "Curated rows are retained with invalid mapped fields nullified where possible.\n",
        encoding="utf-8",
    )
    metadata = pd.DataFrame()
    if files["metadata"]:
        metadata = read_csv_strings(files["metadata"][0])
        metadata["year"] = metadata["year"].map(to_int_nullable).astype("Int64")
        metadata = metadata.drop_duplicates("match_id", keep="first")
    meta_cols = ["match_id", "year", "slam", "match_num", "player1", "player2", "event_name", "round", "status", "source_file"]
    metadata_join = metadata.reindex(columns=meta_cols)
    part_paths = []
    quarantine_parts = []
    invalid_metadata_parts = []
    event_counts: Dict[str, int] = {}
    metrics = {
        "curated_singles_point_rows": 0,
        "curated_singles_match_count": 0,
        "duplicate_event_id_count": 0,
        "missing_match_id_count": 0,
        "missing_event_id_count": 0,
        "metadata_join_success_count": 0,
        "metadata_join_missing_count": 0,
        "invalid_point_winner_count": 0,
        "invalid_point_server_count": 0,
        "special_point_number_count": 0,
        "missing_elapsed_time_count": 0,
        "missing_rally_length_count": 0,
        "missing_surface_count": 0,
        "quarantined_row_count": 0,
    }
    seen_event_ids = set()
    all_matches: List[pd.DataFrame] = []
    for part_idx, path in enumerate(files["singles"]):
        points = read_csv_strings(path)
        points = points.reindex(columns=POINT_COLUMNS)
        points["_input_file"] = str(path.relative_to(input_path))
        points["_source_row_number"] = range(len(points))
        points["_event_order"] = points["event_id"].map(parse_event_suffix)
        points["_event_order"] = points["_event_order"].fillna(points["_source_row_number"]).astype("int64")
        points = points.sort_values(["match_id", "_event_order", "_source_row_number"], kind="mergesort").reset_index(drop=True)
        merged = points.merge(metadata_join, on="match_id", how="left", suffixes=("", "_metadata"))
        pwin_code = merged["PointWinner"].map(normalize_code)
        pserver_code = merged["PointServer"].map(normalize_code)
        invalid_winner = merged["PointWinner"].map(is_invalid_code)
        invalid_server = merged["PointServer"].map(is_invalid_code)
        special_point = merged["PointNumber"].map(row_has_invalid_point_number)
        p1_missing = merged["player1"].isna() | (merged["player1"].astype("string").str.len() == 0)
        p2_missing = merged["player2"].isna() | (merged["player2"].astype("string").str.len() == 0)
        metadata_missing = p1_missing | p2_missing
        event_missing = merged["event_id"].map(norm_text).isna()
        match_missing = merged["match_id"].map(norm_text).isna()
        duplicates_in_part = merged["event_id"].duplicated(keep="first") & ~event_missing
        duplicate_global = merged["event_id"].map(lambda x: norm_text(x) in seen_event_ids if norm_text(x) else False)
        for eid in merged["event_id"]:
            s = norm_text(eid)
            if s:
                seen_event_ids.add(s)
        metrics["missing_match_id_count"] += int(match_missing.sum())
        metrics["missing_event_id_count"] += int(event_missing.sum())
        metrics["duplicate_event_id_count"] += int(duplicates_in_part.sum() + duplicate_global.sum())
        metrics["metadata_join_success_count"] += int((~metadata_missing).sum())
        metrics["metadata_join_missing_count"] += int(metadata_missing.sum())
        metrics["invalid_point_winner_count"] += int(invalid_winner.sum())
        metrics["invalid_point_server_count"] += int(invalid_server.sum())
        metrics["special_point_number_count"] += int(special_point.sum())
        metrics["missing_elapsed_time_count"] += int(merged["ElapsedTime"].map(norm_text).isna().sum())
        metrics["missing_rally_length_count"] += int(merged["Rally"].map(norm_text).isna().sum())
        p1 = pd.Series(
            [participant_name(v, mid, 1) for v, mid in zip(merged["player1"], merged["match_id"])],
            index=merged.index,
        )
        p2 = pd.Series(
            [participant_name(v, mid, 2) for v, mid in zip(merged["player2"], merged["match_id"])],
            index=merged.index,
        )
        curated = pd.DataFrame(
            {
                "event_id": merged["event_id"].map(norm_text),
                "match_id": merged["match_id"].map(norm_text),
                "source_match_id": merged["match_id"].map(norm_text),
                "year": merged["year"],
                "slam": merged["slam"].map(norm_text),
                "tournament": merged["event_name"].map(norm_text),
                "surface": pd.NA,
                "player_a": p1.map(norm_text),
                "player_b": p2.map(norm_text),
                "server_player": [map_player(c, a, b) for c, a, b in zip(pserver_code, p1, p2)],
                "receiver_player": [receiver_for_server(c, a, b) for c, a, b in zip(pserver_code, p1, p2)],
                "point_winner_player": [map_player(c, a, b) for c, a, b in zip(pwin_code, p1, p2)],
                "set_number": merged["SetNo"].map(to_int_nullable),
                "game_number": merged["GameNo"].map(to_int_nullable),
                "point_number": merged["PointNumber"].map(to_int_nullable),
                "p1_score": merged["P1Score"].map(norm_text),
                "p2_score": merged["P2Score"].map(norm_text),
                "p1_games_won": merged["P1GamesWon"].map(to_int_nullable),
                "p2_games_won": merged["P2GamesWon"].map(to_int_nullable),
                "rally_length": merged["Rally"].map(to_int_nullable),
                "serve_speed_kmh": merged["Speed_KMH"].map(to_float_nullable),
                "serve_speed_mph": merged["Speed_MPH"].map(to_float_nullable),
                "is_ace": add_bool_pair(merged, "P1Ace", "P2Ace"),
                "is_double_fault": add_bool_pair(merged, "P1DoubleFault", "P2DoubleFault"),
                "is_break_point": add_bool_pair(merged, "P1BreakPoint", "P2BreakPoint"),
                "elapsed_seconds": merged["ElapsedTime"].map(parse_elapsed_seconds),
                "source_file": merged["source_file"].map(norm_text),
                "schema_version": SCHEMA_VERSION,
                "replay_session_id": pd.NA,
                "synthetic_match_id": pd.NA,
                "event_ts": pd.NaT,
            }
        )
        # Deterministic event_index across possible split files.
        indexes = []
        for mid in curated["match_id"]:
            key = norm_text(mid) or "__missing__"
            indexes.append(event_counts.get(key, 0))
            event_counts[key] = event_counts.get(key, 0) + 1
        curated["event_index"] = indexes
        curated = coerce_curated_types(curated)
        metrics["missing_surface_count"] += int(curated["surface"].isna().sum())
        metrics["curated_singles_point_rows"] += len(curated)
        part_path = out_path / "singles_points" / f"part-{part_idx:05d}.parquet"
        write_parquet(curated, part_path)
        part_paths.append(part_path)
        qmask = invalid_winner | invalid_server | special_point
        if qmask.any():
            q = merged.loc[qmask, :].copy()
            q["invalid_point_winner"] = invalid_winner.loc[qmask].to_numpy()
            q["invalid_point_server"] = invalid_server.loc[qmask].to_numpy()
            q["special_point_number"] = special_point.loc[qmask].to_numpy()
            q["input_file"] = str(path.relative_to(input_path))
            qpath = quarantine_path / "invalid_points" / f"part-{part_idx:05d}.parquet"
            write_parquet(q, qpath)
            quarantine_parts.append(qpath)
            metrics["quarantined_row_count"] += len(q)
        if metadata_missing.any():
            im = merged.loc[metadata_missing, :].copy()
            im["missing_player1"] = p1_missing.loc[metadata_missing].to_numpy()
            im["missing_player2"] = p2_missing.loc[metadata_missing].to_numpy()
            im["input_file"] = str(path.relative_to(input_path))
            im_path = quarantine_path / "invalid_metadata" / f"part-{part_idx:05d}.parquet"
            write_parquet(im, im_path)
            invalid_metadata_parts.append(im_path)
        match_snapshot = curated[["match_id", "year", "slam", "tournament", "surface", "player_a", "player_b", "source_file"]].drop_duplicates("match_id")
        all_matches.append(match_snapshot)
    matches = pd.concat(all_matches, ignore_index=True).drop_duplicates("match_id").sort_values("match_id").reset_index(drop=True)
    metrics["curated_singles_match_count"] = int(len(matches))
    write_parquet(matches, out_path / "singles_matches" / "part-00000.parquet")
    replay = pd.DataFrame(
        {
            "match_id": matches["match_id"],
            "replay_ready": True,
            "reason": "static_order_only_event_ts_created_later",
            "schema_version": SCHEMA_VERSION,
        }
    )
    write_parquet(replay, out_path / "replay_candidates" / "part-00000.parquet")
    write_json(
        out_path / "zone_metadata.json",
        {
            "zone": "curated",
            "schema_version": SCHEMA_VERSION,
            "generated_at": now_iso(),
            "format": "parquet",
            "datasets": {
                "singles_points_parts": len(part_paths),
                "singles_matches_parts": 1,
                "replay_candidates_parts": 1,
            },
        },
    )
    write_json(
        quarantine_path / "zone_metadata.json",
        {
            "zone": "quarantine",
            "schema_version": SCHEMA_VERSION,
            "generated_at": now_iso(),
            "invalid_points_parts": len(quarantine_parts),
            "invalid_metadata_parts": len(invalid_metadata_parts),
        },
    )
    return metrics


def read_parquet_dir(path: Path) -> pd.DataFrame:
    parts = sorted(path.glob("part-*.parquet"))
    if not parts:
        return pd.DataFrame()
    return pd.concat([pd.read_parquet(p, engine="pyarrow") for p in parts], ignore_index=True)


def generate_reports(input_path: Path, cleaned_path: Path, curated_path: Path, quarantine_path: Path, root: Path) -> Dict[str, Any]:
    inventory = inspect_inputs(input_path)
    singles = read_parquet_dir(curated_path / "singles_points")
    metrics_path = curated_path / "_curated_metrics.json"
    metrics = read_json(metrics_path) if metrics_path.exists() else {}
    raw_metadata_rows = 0
    raw_atp_rows = 0
    files = discover_inputs(input_path)
    if files["metadata"]:
        raw_metadata_rows = csv_gz_header_and_count(files["metadata"][0])[1]
    if files["atp"]:
        raw_atp_rows = csv_gz_header_and_count(files["atp"][0])[1]
    warnings = []
    blocking_errors = []
    if int(metrics.get("missing_surface_count", 0)) > 0:
        warnings.append("surface is unavailable in match metadata and is null in curated singles output")
    if int(metrics.get("missing_rally_length_count", 0)) > 0:
        warnings.append("rally length coverage is sparse and should not be a primary MVP feature")
    if int(metrics.get("invalid_point_winner_count", 0)) > 0 or int(metrics.get("invalid_point_server_count", 0)) > 0:
        warnings.append("invalid point winner/server codes were nullified and copied to quarantine evidence")
    report = {
        "generated_at": now_iso(),
        "input_archive": str(input_path),
        "schema_version": SCHEMA_VERSION,
        "total_files_seen": inventory["total_files_seen"],
        "point_files_seen": inventory["point_files_seen"],
        "metadata_files_seen": inventory["metadata_files_seen"],
        "atp_match_files_seen": inventory["atp_match_files_seen"],
        "raw_point_rows": inventory["raw_point_rows"],
        "raw_metadata_rows": raw_metadata_rows,
        "raw_atp_match_rows": raw_atp_rows,
        "curated_singles_point_rows": int(metrics.get("curated_singles_point_rows", len(singles))),
        "curated_singles_match_count": int(metrics.get("curated_singles_match_count", singles["match_id"].nunique() if not singles.empty else 0)),
        "excluded_doubles_files": inventory["doubles_point_files_seen"],
        "excluded_doubles_rows": inventory["excluded_doubles_rows"],
        "excluded_mixed_files": inventory["mixed_point_files_seen"],
        "excluded_mixed_rows": inventory["excluded_mixed_rows"],
        "duplicate_event_id_count": int(metrics.get("duplicate_event_id_count", 0)),
        "missing_match_id_count": int(metrics.get("missing_match_id_count", 0)),
        "missing_event_id_count": int(metrics.get("missing_event_id_count", 0)),
        "metadata_join_success_count": int(metrics.get("metadata_join_success_count", 0)),
        "metadata_join_missing_count": int(metrics.get("metadata_join_missing_count", 0)),
        "invalid_point_winner_count": int(metrics.get("invalid_point_winner_count", 0)),
        "invalid_point_server_count": int(metrics.get("invalid_point_server_count", 0)),
        "special_point_number_count": int(metrics.get("special_point_number_count", 0)),
        "missing_elapsed_time_count": int(metrics.get("missing_elapsed_time_count", 0)),
        "missing_rally_length_count": int(metrics.get("missing_rally_length_count", 0)),
        "missing_surface_count": int(metrics.get("missing_surface_count", 0)),
        "quarantined_row_count": int(metrics.get("quarantined_row_count", 0)),
        "schema_inventory": inventory["schema_variants"],
        "warnings": warnings,
        "blocking_errors": blocking_errors,
    }
    write_json(cleaned_path / "data_quality_report.json", report)
    write_json(curated_path / "data_quality_report.json", report)
    feature_report = build_feature_report(report, singles)
    write_json(cleaned_path / "feature_availability_report.json", feature_report)
    docs(root, report, feature_report)
    return report


def availability(df: pd.DataFrame, cols: Sequence[str]) -> Tuple[float, int]:
    if df.empty:
        return 0.0, 0
    present = pd.Series(True, index=df.index)
    for col in cols:
        present = present & df[col].notna()
    missing = int((~present).sum())
    return round(float(present.mean() * 100), 4), missing


def build_feature_report(report: Dict[str, Any], singles: pd.DataFrame) -> Dict[str, Any]:
    specs = [
        ("serve win features", ["server_player", "point_winner_player"], True, "Derivable from server and point winner mapping when both are valid."),
        ("ace features", ["is_ace"], True, "Available from P1Ace/P2Ace normalized booleans."),
        ("double fault features", ["is_double_fault"], True, "Available from P1DoubleFault/P2DoubleFault normalized booleans."),
        ("break point features", ["is_break_point"], True, "Available from P1BreakPoint/P2BreakPoint normalized booleans."),
        ("rally length features", ["rally_length"], False, "Sparse coverage; report but do not use as a primary MVP feature."),
        ("elapsed time features", ["elapsed_seconds"], True, "Missing for some rows but event_index preserves ordering."),
        ("player metadata features", ["player_a", "player_b"], True, "Metadata join covers inspected singles matches."),
        ("surface/tournament features", ["surface", "tournament"], False, "Tournament exists; surface is unavailable in metadata."),
        ("score context features", ["p1_score", "p2_score", "p1_games_won", "p2_games_won"], True, "Score and game context are present for MVP state features."),
    ]
    features = []
    for name, cols, usable, notes in specs:
        pct, missing = availability(singles, cols)
        if name == "rally length features" and pct < 50:
            usable = False
        if name == "surface/tournament features" and report.get("missing_surface_count", 0) > 0:
            usable = False
        features.append(
            {
                "feature_name": name,
                "source_columns": cols,
                "availability_percent": pct,
                "missing_count": missing,
                "usable_for_mvp": usable,
                "notes": notes,
            }
        )
    return {
        "generated_at": now_iso(),
        "schema_version": SCHEMA_VERSION,
        "features": features,
    }


def docs(root: Path, report: Dict[str, Any], feature_report: Dict[str, Any]) -> None:
    docs_dir = root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    verdict = "PASSED" if not report["blocking_errors"] else "FAILED"
    (docs_dir / "data_layer_audit.md").write_text(
        f"""# Data Layer Audit

## Executive Verdict

Milestone 1B status: **{verdict}**.

The teammate-provided CSV.GZ files were treated as staging input. The project-compliant outputs are Parquet datasets under `data/cleaned/` and `data/curated/`, with quarantine evidence under `data/quarantine/`.

## Input Inventory

- Total CSV.GZ files seen: {report['total_files_seen']}
- Point files seen: {report['point_files_seen']}
- Metadata files seen: {report['metadata_files_seen']}
- ATP match files seen: {report['atp_match_files_seen']}
- Raw point rows: {report['raw_point_rows']}
- Raw metadata rows: {report['raw_metadata_rows']}
- Raw ATP match rows: {report['raw_atp_match_rows']}

## Transformations

- Singles point files were converted to canonical curated point Parquet.
- Doubles and mixed files were excluded from MVP curated singles output.
- `PointWinner` and `PointServer` values `1`, `1.0`, `2`, and `2.0` were normalized to players; invalid codes were counted and nullified in mapped player fields.
- Special non-integer `PointNumber` values were counted, nullified in `point_number`, and copied to quarantine evidence.
- `ElapsedTime` was parsed to `elapsed_seconds` where possible.
- Metadata was joined by `match_id`; ATP matches were preserved as cleaned Parquet without a forced unreliable join.
- Rows with blank `player1` or `player2` metadata were preserved using deterministic `unknown_player_1:<match_id>` / `unknown_player_2:<match_id>` participant placeholders and copied to invalid metadata quarantine evidence.

## Exclusions And Quarantine

- Excluded doubles files: {report['excluded_doubles_files']}
- Excluded doubles rows: {report['excluded_doubles_rows']}
- Excluded mixed files: {report['excluded_mixed_files']}
- Excluded mixed rows: {report['excluded_mixed_rows']}
- Quarantined evidence rows: {report['quarantined_row_count']}

## Quality Results

- Curated singles point rows: {report['curated_singles_point_rows']}
- Curated singles match count: {report['curated_singles_match_count']}
- Duplicate event IDs: {report['duplicate_event_id_count']}
- Missing event IDs: {report['missing_event_id_count']}
- Missing match IDs: {report['missing_match_id_count']}
- Metadata join missing rows: {report['metadata_join_missing_count']}
- Invalid PointWinner values: {report['invalid_point_winner_count']}
- Invalid PointServer values: {report['invalid_point_server_count']}
- Special PointNumber values: {report['special_point_number_count']}
- Missing elapsed time rows: {report['missing_elapsed_time_count']}
- Missing rally length rows: {report['missing_rally_length_count']}
- Missing surface rows: {report['missing_surface_count']}

## Remaining Risks

- Surface is not present in `match_metadata_cleaned.csv.gz`, so curated `surface` is null.
- Some metadata rows have blank player slots. The curated layer keeps those rows with deterministic unknown-player placeholders and quarantines the original rows for review.
- Rally length coverage is sparse and should not be a primary MVP feature.
- ATP match data is preserved but not joined to point events until a reliable bridge is defined.
- Static curated data intentionally leaves `event_ts` null; replay timestamps belong to the later replay milestone.
""",
        encoding="utf-8",
    )
    (docs_dir / "data_cleaning_decisions.md").write_text(
        """# Data Cleaning Decisions

- `cleaned_data/` is staging input, not final cleaned output.
- MVP curated data is singles only; doubles and mixed are excluded by filename classification and counted.
- Invalid `PointWinner`/`PointServer` codes are not silently cast. Valid values are `1`, `1.0`, `2`, and `2.0`; all other non-empty values are invalid and mapped player fields are set to null.
- Non-integer `PointNumber` values such as `0X`, `0Y`, and `45D` are not forced to integers. They are counted, copied to quarantine evidence, and represented as null in canonical `point_number`.
- `event_index` is deterministic by `match_id`, source event suffix when present, and source row order.
- ATP match data is written as cleaned Parquet but not forced into curated points because there is no inspected reliable key bridge.
- Blank `player1` or `player2` metadata values are not dropped or fabricated as real names. They are replaced with deterministic unknown-player participant placeholders in curated output and copied to `data/quarantine/invalid_metadata/`.
- No fraud labels, model labels, or anomaly labels are created in Milestone 1B.
""",
        encoding="utf-8",
    )
    (docs_dir / "next_implementation_steps.md").write_text(
        f"""# Next Implementation Steps

Milestone 1B status: **{verdict}**.

If validation passes, the next milestone is feature engineering on top of `data/curated/singles_points/`, followed by baseline generation and replay manifest preparation.

Recommended next steps:

1. Build point-in-time-safe rolling features from curated singles points.
2. Build player baselines using only prior points/matches relative to each event.
3. Create replay manifests that assign synthetic match IDs and replay timestamps.
4. Keep model training blocked until feature and baseline validation pass.

Do not start Kafka, streaming, FastAPI, React, or model training from staging CSVs.
""",
        encoding="utf-8",
    )


def validate_layer(cleaned_path: Path, curated_path: Path, contracts_path: Path) -> Dict[str, Any]:
    errors = []
    points_dir = curated_path / "singles_points"
    if not sorted(points_dir.glob("part-*.parquet")):
        errors.append("curated singles points Parquet files are missing")
        points = pd.DataFrame()
    else:
        points = read_parquet_dir(points_dir)
    required_files = [
        cleaned_path / "data_quality_report.json",
        cleaned_path / "feature_availability_report.json",
        curated_path / "data_quality_report.json",
        curated_path / "zone_metadata.json",
        contracts_path / "curated_point_schema.json",
        contracts_path / "data_quality_report_schema.json",
        Path("docs/data_layer_audit.md"),
    ]
    for path in required_files:
        if not path.exists():
            errors.append(f"missing required file: {path}")
    if not points.empty:
        for col in CURATED_POINT_COLUMNS:
            if col not in points.columns:
                errors.append(f"missing curated column: {col}")
        if points["event_id"].isna().any() or (points["event_id"].astype("string").str.len() == 0).any():
            errors.append("curated points contain null/blank event_id")
        if points["match_id"].isna().any() or (points["match_id"].astype("string").str.len() == 0).any():
            errors.append("curated points contain null/blank match_id")
        if points["player_a"].isna().any() or (points["player_a"].astype("string").str.len() == 0).any():
            errors.append("curated points contain null/blank player_a")
        if points["player_b"].isna().any() or (points["player_b"].astype("string").str.len() == 0).any():
            errors.append("curated points contain null/blank player_b")
        dup = int(points["event_id"].duplicated().sum())
        if dup:
            errors.append(f"curated points contain duplicate event_id values: {dup}")
        if points["event_index"].isna().any():
            errors.append("curated points contain null event_index")
        ordered = points.sort_values(["match_id", "event_index"], kind="mergesort")
        bad_order = ordered.groupby("match_id")["event_index"].apply(lambda s: not (s.to_numpy() == range(len(s))).all())
        if bool(bad_order.any()):
            errors.append("event_index is not contiguous from zero within every match")
        source_files = points["source_file"].astype("string")
        if source_files.str.contains("doubles", case=False, na=False).any() or source_files.str.contains("mixed", case=False, na=False).any():
            errors.append("curated singles output includes doubles or mixed source files")
        valid_server_winner = points["server_player"].notna().sum() > 0 and points["point_winner_player"].notna().sum() > 0
        if not valid_server_winner:
            errors.append("server_player or point_winner_player mappings are empty")
    report_path = cleaned_path / "data_quality_report.json"
    if report_path.exists():
        report = read_json(report_path)
        for key in REPORT_KEYS:
            if key not in report:
                errors.append(f"data quality report missing key: {key}")
        if report.get("blocking_errors"):
            errors.extend(report["blocking_errors"])
    result = {
        "generated_at": now_iso(),
        "status": "PASSED" if not errors else "FAILED",
        "blocking_errors": errors,
        "curated_singles_point_rows": int(len(points)),
        "curated_singles_match_count": int(points["match_id"].nunique()) if not points.empty and "match_id" in points else 0,
    }
    write_json(curated_path / "validation_report.json", result)
    if errors:
        raise SystemExit(json.dumps(result, indent=2, sort_keys=True))
    return result


def parser_with_io(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--input", type=Path, default=Path("cleaned_data"))
    parser.add_argument("--out", type=Path)
    parser.add_argument("--cleaned", type=Path, default=Path("data/cleaned"))
    parser.add_argument("--curated", type=Path, default=Path("data/curated"))
    parser.add_argument("--quarantine", type=Path, default=Path("data/quarantine"))
    parser.add_argument("--contracts", type=Path, default=Path("contracts"))
    return parser
