#!/usr/bin/env python3
"""Build Milestone 2A player baseline Parquet outputs."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

BASELINE_SCHEMA_VERSION = "2A.1.0"

PLAYER_BASELINE_COLUMNS = [
    "player",
    "total_matches",
    "total_points",
    "serve_points",
    "serve_points_won",
    "serve_point_win_pct",
    "return_points",
    "return_points_won",
    "return_point_win_pct",
    "aces",
    "double_faults",
    "ace_rate",
    "double_fault_rate",
    "avg_serve_speed_kmh",
    "rally_length_avg",
    "rally_length_available_pct",
    "elapsed_time_available_pct",
    "baseline_quality_level",
    "is_unknown_placeholder",
    "baseline_schema_version",
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


def is_unknown_name(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("unknown_player_")


def quality_level(total_points: int, is_placeholder: bool) -> str:
    if is_placeholder:
        return "invalid_or_placeholder"
    if total_points >= 200:
        return "strong"
    if total_points >= 50:
        return "moderate"
    return "weak"


def build_baselines(points: pd.DataFrame) -> pd.DataFrame:
    if points.empty:
        return pd.DataFrame(columns=PLAYER_BASELINE_COLUMNS)
    df = points.sort_values(["match_id", "event_index", "event_id"], kind="mergesort").copy()
    player_a = df["player_a"].astype("string")
    player_b = df["player_b"].astype("string")
    winner = df["point_winner_player"].astype("string")
    server = df["server_player"].astype("string")
    receiver = df["receiver_player"].astype("string")
    df["_valid_winner"] = (winner.eq(player_a) | winner.eq(player_b)).fillna(False)
    df["_valid_server"] = (server.eq(player_a) | server.eq(player_b)).fillna(False)
    df["_server_won"] = (df["_valid_winner"] & df["_valid_server"] & server.eq(winner).fillna(False))
    df["_receiver_won"] = (df["_valid_winner"] & df["_valid_server"] & receiver.eq(winner).fillna(False))
    df["_ace"] = df["is_ace"].fillna(False).astype(bool)
    df["_double_fault"] = df["is_double_fault"].fillna(False).astype(bool)
    involved_a = df[["match_id", "player_a", "rally_length", "elapsed_seconds", "_valid_winner"]].rename(columns={"player_a": "player"})
    involved_b = df[["match_id", "player_b", "rally_length", "elapsed_seconds", "_valid_winner"]].rename(columns={"player_b": "player"})
    involved = pd.concat([involved_a, involved_b], ignore_index=True)
    involved["valid_point_int"] = involved["_valid_winner"].astype("int64")
    involved["rally_present"] = involved["rally_length"].notna().astype("int64")
    involved["elapsed_present"] = involved["elapsed_seconds"].notna().astype("int64")

    total = (
        involved.groupby("player", dropna=True)
        .agg(
            total_matches=("match_id", "nunique"),
            total_points=("valid_point_int", "sum"),
            rally_length_avg=("rally_length", "mean"),
            rally_present=("rally_present", "sum"),
            elapsed_present=("elapsed_present", "sum"),
            involved_rows=("match_id", "size"),
        )
        .reset_index()
    )
    total["rally_length_available_pct"] = total["rally_present"] / total["involved_rows"].where(total["involved_rows"] != 0) * 100
    total["elapsed_time_available_pct"] = total["elapsed_present"] / total["involved_rows"].where(total["involved_rows"] != 0) * 100

    serve = df.loc[df["_valid_server"], ["server_player", "_server_won", "_ace", "_double_fault", "serve_speed_kmh"]].rename(columns={"server_player": "player"})
    serve["_server_won_int"] = serve["_server_won"].astype("int64")
    serve["_ace_int"] = serve["_ace"].astype("int64")
    serve["_double_fault_int"] = serve["_double_fault"].astype("int64")
    serve_agg = (
        serve.groupby("player", dropna=True)
        .agg(
            serve_points=("player", "size"),
            serve_points_won=("_server_won_int", "sum"),
            aces=("_ace_int", "sum"),
            double_faults=("_double_fault_int", "sum"),
            avg_serve_speed_kmh=("serve_speed_kmh", "mean"),
        )
        .reset_index()
    )

    ret = df.loc[df["_valid_server"], ["receiver_player", "_receiver_won"]].rename(columns={"receiver_player": "player"})
    ret["_receiver_won_int"] = ret["_receiver_won"].astype("int64")
    ret_agg = (
        ret.groupby("player", dropna=True)
        .agg(return_points=("player", "size"), return_points_won=("_receiver_won_int", "sum"))
        .reset_index()
    )

    out = total.merge(serve_agg, on="player", how="left").merge(ret_agg, on="player", how="left")
    for col in ["serve_points", "serve_points_won", "aces", "double_faults", "return_points", "return_points_won"]:
        out[col] = out[col].fillna(0).astype("int64")
    out["serve_point_win_pct"] = (out["serve_points_won"] / out["serve_points"].where(out["serve_points"] != 0)).fillna(0.0)
    out["return_point_win_pct"] = (out["return_points_won"] / out["return_points"].where(out["return_points"] != 0)).fillna(0.0)
    out["ace_rate"] = (out["aces"] / out["serve_points"].where(out["serve_points"] != 0)).fillna(0.0)
    out["double_fault_rate"] = (out["double_faults"] / out["serve_points"].where(out["serve_points"] != 0)).fillna(0.0)
    out["is_unknown_placeholder"] = out["player"].map(is_unknown_name)
    out["baseline_quality_level"] = [
        quality_level(int(total_points), bool(is_placeholder))
        for total_points, is_placeholder in zip(out["total_points"], out["is_unknown_placeholder"])
    ]
    out["baseline_schema_version"] = BASELINE_SCHEMA_VERSION
    out = out.drop(columns=["rally_present", "elapsed_present", "involved_rows"])
    return out.sort_values(["baseline_quality_level", "player"]).reset_index(drop=True)[PLAYER_BASELINE_COLUMNS]


def write_contract(contracts: Path) -> None:
    props: Dict[str, Any] = {
        "player": {"type": "string"},
        "baseline_quality_level": {"type": "string"},
        "is_unknown_placeholder": {"type": "boolean"},
        "baseline_schema_version": {"type": "string"},
    }
    for col in ["total_matches", "total_points", "serve_points", "serve_points_won", "return_points", "return_points_won", "aces", "double_faults"]:
        props[col] = {"type": "integer"}
    for col in ["serve_point_win_pct", "return_point_win_pct", "ace_rate", "double_fault_rate", "avg_serve_speed_kmh", "rally_length_avg", "rally_length_available_pct", "elapsed_time_available_pct"]:
        props[col] = {"type": ["number", "null"]}
    write_json(
        contracts / "player_baseline_schema.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "PlayerBaseline",
            "type": "object",
            "required": PLAYER_BASELINE_COLUMNS,
            "additionalProperties": True,
            "properties": props,
        },
    )


def write_docs(path: Path, report: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""# Baseline Generation Audit

## Baseline Logic

Player baselines were computed from curated singles point events. Each player receives match count, point volume, serve/return win rates, ace and double-fault rates, serve-speed averages, rally availability, and elapsed-time availability.

## Sample Thresholds

- `strong`: `total_points >= 200`
- `moderate`: `total_points >= 50`
- `weak`: `total_points < 50`
- `invalid_or_placeholder`: deterministic unknown-player placeholders, regardless of sample size

## Unknown-Player Handling

Unknown placeholders are retained for auditability but are never assigned strong baselines. Placeholder count: {report['placeholder_player_count']}.

## Surface And Rally Limitations

Surface-specific baselines are blocked because curated surface metadata is unavailable. Rally averages are sparse and should remain secondary until coverage improves.

## Quality Distribution

- Players: {report['player_count']}
- Strong: {report['strong_baseline_count']}
- Moderate: {report['moderate_baseline_count']}
- Weak: {report['weak_baseline_count']}
- Placeholder: {report['placeholder_player_count']}
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, default=Path("data/features"))
    parser.add_argument("--curated", type=Path, default=Path("data/curated"))
    parser.add_argument("--out", type=Path, default=Path("data/baselines"))
    parser.add_argument("--contracts", type=Path, default=Path("contracts"))
    parser.add_argument("--max-matches", type=int)
    args = parser.parse_args()

    points = read_parquet_dir(args.curated / "singles_points", args.max_matches)
    if points.empty:
        raise SystemExit("No curated singles points found.")
    baselines = build_baselines(points)
    clean_dir(args.out / "player_baselines")
    baselines.to_parquet(args.out / "player_baselines" / "part-00000.parquet", index=False, engine="pyarrow")
    write_contract(args.contracts)

    report = {
        "generated_at": now_iso(),
        "input_dataset": str(args.curated / "singles_points"),
        "output_dataset": str(args.out / "player_baselines"),
        "baseline_schema_version": BASELINE_SCHEMA_VERSION,
        "player_count": int(len(baselines)),
        "strong_baseline_count": int((baselines["baseline_quality_level"] == "strong").sum()),
        "moderate_baseline_count": int((baselines["baseline_quality_level"] == "moderate").sum()),
        "weak_baseline_count": int((baselines["baseline_quality_level"] == "weak").sum()),
        "placeholder_player_count": int(baselines["is_unknown_placeholder"].sum()),
        "missing_serve_data_count": int((baselines["serve_points"] == 0).sum()),
        "missing_return_data_count": int((baselines["return_points"] == 0).sum()),
        "rally_sparse_warning": "rally_length coverage is sparse; rally baselines are secondary",
        "surface_unavailable_warning": "surface-specific baselines are blocked until metadata improves",
    }
    write_json(args.out / "baseline_quality_report.json", report)
    write_json(
        args.out / "zone_metadata.json",
        {
            "zone": "baselines",
            "schema_version": BASELINE_SCHEMA_VERSION,
            "generated_at": now_iso(),
            "format": "parquet",
            "datasets": {"player_baselines_parts": 1},
        },
    )
    write_docs(Path("docs/baseline_generation_audit.md"), report)
    print(f"wrote player baselines={len(baselines)} to {args.out}")


if __name__ == "__main__":
    main()
