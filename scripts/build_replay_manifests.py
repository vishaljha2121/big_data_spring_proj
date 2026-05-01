#!/usr/bin/env python3
"""Prepare deterministic Milestone 2A replay manifests without starting Kafka."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

REPLAY_SCHEMA_VERSION = "2A.1.0"

REPLAY_COLUMNS = [
    "replay_session_id",
    "synthetic_match_id",
    "source_match_id",
    "event_id",
    "synthetic_event_id",
    "event_index",
    "replay_order",
    "replay_offset_seconds",
    "event_ts",
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
    "is_ace",
    "is_double_fault",
    "is_break_point",
    "source_file",
    "replay_schema_version",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def read_parquet_dir(path: Path, max_matches: Optional[int] = None) -> pd.DataFrame:
    parts = sorted(path.glob("part-*.parquet"))
    if not parts:
        return pd.DataFrame()
    df = pd.concat([pd.read_parquet(part, engine="pyarrow") for part in parts], ignore_index=True)
    if max_matches is not None and "match_id" in df:
        keep = sorted(df["match_id"].dropna().astype(str).unique())[:max_matches]
        df = df[df["match_id"].astype(str).isin(keep)].copy()
    return df


def stable_id(prefix: str, *parts: Any, length: int = 16) -> str:
    raw = "|".join("" if part is None or pd.isna(part) else str(part) for part in parts)
    return f"{prefix}_{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:length]}"


def has_unknown_players(group: pd.DataFrame) -> bool:
    return bool(
        group["player_a"].astype("string").str.startswith("unknown_player_", na=False).any()
        or group["player_b"].astype("string").str.startswith("unknown_player_", na=False).any()
    )


def valid_point_count(group: pd.DataFrame) -> int:
    player_a = group["player_a"].astype("string")
    player_b = group["player_b"].astype("string")
    winner = group["point_winner_player"].astype("string")
    return int((winner.eq(player_a).fillna(False) | winner.eq(player_b).fillna(False)).sum())


def offsets_for_group(group: pd.DataFrame, default_interval: float) -> List[float]:
    offsets: List[float] = []
    last = 0.0
    for idx, value in enumerate(group["elapsed_seconds"]):
        if pd.notna(value):
            candidate = float(value)
            if idx == 0:
                last = max(0.0, candidate)
            else:
                last = candidate if candidate >= last else last + default_interval
        else:
            last = 0.0 if idx == 0 else last + default_interval
        offsets.append(last)
    return offsets


def build_replay_manifest(points: pd.DataFrame, seed: int, default_interval_seconds: float) -> Dict[str, Any]:
    if points.empty:
        return {"manifest": pd.DataFrame(columns=REPLAY_COLUMNS), "candidates": pd.DataFrame(), "excluded": []}
    df = points.sort_values(["match_id", "event_index", "event_id"], kind="mergesort").copy()
    replay_session_id = f"replay_session_v1_seed_{seed}"
    included_frames = []
    candidate_rows = []
    excluded = []
    base_ts = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for match_id, group in df.groupby("match_id", sort=True):
        group = group.sort_values(["event_index", "event_id"], kind="mergesort").copy()
        unknown = has_unknown_players(group)
        valid_points = valid_point_count(group)
        if unknown:
            reason = "unknown_player_placeholder"
        elif valid_points < 20:
            reason = "fewer_than_20_valid_points"
        else:
            reason = "included"
        ready = reason == "included"
        candidate_rows.append(
            {
                "match_id": match_id,
                "replay_ready": ready,
                "reason": reason,
                "valid_points": valid_points,
                "has_unknown_player": unknown,
                "replay_schema_version": REPLAY_SCHEMA_VERSION,
            }
        )
        if not ready:
            excluded.append({"match_id": match_id, "reason": reason, "valid_points": valid_points})
            continue
        synthetic_match_id = stable_id("synthetic_match", match_id, seed)
        group["replay_session_id"] = replay_session_id
        group["synthetic_match_id"] = synthetic_match_id
        group["source_match_id"] = group["match_id"]
        group["synthetic_event_id"] = [
            stable_id("synthetic_event", synthetic_match_id, row.event_id, row.event_index, seed, length=24)
            for row in group[["event_id", "event_index"]].itertuples(index=False)
        ]
        group["replay_order"] = range(len(group))
        group["replay_offset_seconds"] = offsets_for_group(group, default_interval_seconds)
        group["event_ts"] = [
            (base_ts + timedelta(seconds=float(offset))).isoformat().replace("+00:00", "Z")
            for offset in group["replay_offset_seconds"]
        ]
        group["replay_schema_version"] = REPLAY_SCHEMA_VERSION
        included_frames.append(group)
    manifest = pd.concat(included_frames, ignore_index=True) if included_frames else pd.DataFrame(columns=REPLAY_COLUMNS)
    if not manifest.empty:
        manifest = manifest[REPLAY_COLUMNS].sort_values(["synthetic_match_id", "replay_order"], kind="mergesort").reset_index(drop=True)
    candidates = pd.DataFrame(candidate_rows).sort_values("match_id").reset_index(drop=True)
    return {"manifest": manifest, "candidates": candidates, "excluded": excluded, "replay_session_id": replay_session_id}


def write_contract(contracts: Path) -> None:
    props: Dict[str, Any] = {}
    for col in REPLAY_COLUMNS:
        props[col] = {"type": ["string", "null"]}
    for col in ["event_index", "replay_order", "set_number", "game_number", "point_number"]:
        props[col] = {"type": ["integer", "null"]}
    props["replay_offset_seconds"] = {"type": "number"}
    for col in ["is_ace", "is_double_fault", "is_break_point"]:
        props[col] = {"type": ["boolean", "null"]}
    write_json(
        contracts / "replay_manifest_schema.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "ReplayManifestV1",
            "type": "object",
            "required": REPLAY_COLUMNS,
            "additionalProperties": True,
            "properties": props,
        },
    )


def write_docs(path: Path, summary: Dict[str, Any], report: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""# Replay Manifest Audit

## Selection Criteria

Replay candidates were built only from `data/curated/singles_points/`. Matches with deterministic unknown-player placeholders were excluded by default, and matches with fewer than 20 valid point winners were excluded.

## Manifest Schema

The replay manifest schema is stored in `contracts/replay_manifest_schema.json`. The Parquet manifest is `data/replay/manifests/replay_manifest_v1.parquet`.

## Timestamp And Offset Logic

When `elapsed_seconds` is present, it drives `replay_offset_seconds`. Missing elapsed time falls back to `event_index * {summary['default_interval_seconds']}` semantics through a deterministic per-event interval. Offsets are monotonic within each synthetic match. Event timestamps are generated relative to `2026-01-01T00:00:00Z` for deterministic replay preparation.

## Exclusions

Excluded matches: {summary['excluded_match_count']}

## Next Kafka Step

The next milestone may build a Kafka replay producer that reads this manifest in `synthetic_match_id, replay_order` order. Kafka was not started in Milestone 2A.
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--curated", type=Path, default=Path("data/curated"))
    parser.add_argument("--out", type=Path, default=Path("data/replay"))
    parser.add_argument("--contracts", type=Path, default=Path("contracts"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--default-interval-seconds", type=float, default=2.0)
    parser.add_argument("--max-matches", type=int)
    args = parser.parse_args()

    points = read_parquet_dir(args.curated / "singles_points", args.max_matches)
    if points.empty:
        raise SystemExit("No curated singles points found.")
    built = build_replay_manifest(points, args.seed, args.default_interval_seconds)
    manifest: pd.DataFrame = built["manifest"]
    candidates: pd.DataFrame = built["candidates"]
    clean_dir(args.out / "manifests")
    clean_dir(args.out / "replay_candidates")
    manifest.to_parquet(args.out / "manifests" / "replay_manifest_v1.parquet", index=False, engine="pyarrow")
    candidates.to_parquet(args.out / "replay_candidates" / "part-00000.parquet", index=False, engine="pyarrow")
    write_contract(args.contracts)

    limitations = [
        "Kafka replay is not started in this milestone",
        "unknown-player placeholder matches are excluded by default",
        "elapsed_seconds gaps use deterministic default interval offsets",
        "surface remains unavailable",
    ]
    summary = {
        "replay_session_id": built["replay_session_id"],
        "generated_at": now_iso(),
        "source_dataset": str(args.curated / "singles_points"),
        "match_count": int(manifest["synthetic_match_id"].nunique()) if not manifest.empty else 0,
        "event_count": int(len(manifest)),
        "excluded_match_count": int(len(built["excluded"])),
        "default_interval_seconds": args.default_interval_seconds,
        "seed": args.seed,
        "limitations": limitations,
    }
    report = {
        **summary,
        "candidate_match_count": int(len(candidates)),
        "included_match_count": summary["match_count"],
        "excluded_reasons": candidates["reason"].value_counts().to_dict() if not candidates.empty else {},
        "replay_schema_version": REPLAY_SCHEMA_VERSION,
    }
    write_json(args.out / "manifests" / "replay_manifest_v1.json", summary)
    write_json(args.out / "replay_manifest_report.json", report)
    write_json(
        args.out / "zone_metadata.json",
        {
            "zone": "replay",
            "schema_version": REPLAY_SCHEMA_VERSION,
            "generated_at": now_iso(),
            "format": "parquet",
            "datasets": {"manifest_parts": 1, "replay_candidates_parts": 1},
        },
    )
    write_docs(Path("docs/replay_manifest_audit.md"), summary, report)
    print(f"wrote replay manifest events={len(manifest)} matches={summary['match_count']} to {args.out}")


if __name__ == "__main__":
    main()
