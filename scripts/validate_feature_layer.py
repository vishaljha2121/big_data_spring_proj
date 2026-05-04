#!/usr/bin/env python3
"""Validate Milestone 2A feature, baseline, and replay outputs."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from build_feature_layer import POINT_FEATURE_COLUMNS, rolling_prior_pct
from build_player_baselines import PLAYER_BASELINE_COLUMNS
from build_replay_manifests import REPLAY_COLUMNS, stable_id


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_parquet_dir(path: Path) -> pd.DataFrame:
    parts = sorted(path.glob("part-*.parquet"))
    if not parts:
        return pd.DataFrame()
    return pd.concat([pd.read_parquet(part, engine="pyarrow") for part in parts], ignore_index=True)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require_file(path: Path, errors: List[str]) -> None:
    if not path.exists():
        errors.append(f"missing required file: {path}")


def validate_point_features(curated: pd.DataFrame, features: pd.DataFrame, errors: List[str]) -> None:
    if features.empty:
        errors.append("point feature dataset is empty")
        return
    for col in POINT_FEATURE_COLUMNS:
        if col not in features.columns:
            errors.append(f"point feature missing column: {col}")
    for col in ["event_id", "match_id", "event_index"]:
        if features[col].isna().any():
            errors.append(f"point feature contains null {col}")
    dup_events = int(features["event_id"].duplicated().sum())
    if dup_events:
        errors.append(f"event_id is not unique in point features: {dup_events} duplicates")
    if len(features) != len(curated):
        errors.append(f"point feature row count {len(features)} does not equal curated singles point row count {len(curated)}")

    ordered = features.sort_values(["match_id", "event_index", "event_id"], kind="mergesort").reset_index(drop=True)
    first = ordered.groupby("match_id", sort=False).head(1)
    for col in ["points_played_before", "player_a_points_won_before", "player_b_points_won_before"]:
        bad = int((first[col] != 0).sum())
        if bad:
            errors.append(f"first event per match has non-zero {col}: {bad} rows")

    winner = ordered["point_winner_player"].astype("string")
    player_a = ordered["player_a"].astype("string")
    player_b = ordered["player_b"].astype("string")
    valid = (winner.eq(player_a) | winner.eq(player_b)).fillna(False).astype("int64")
    pa_win = (winner.eq(player_a).fillna(False) & valid.astype(bool)).astype("int64")
    pb_win = (winner.eq(player_b).fillna(False) & valid.astype(bool)).astype("int64")
    expected_points = ordered.groupby("match_id", sort=False).cumcount()
    # points_played_before is valid prior outcome count, not raw row count.
    expected_valid_points = valid.groupby(ordered["match_id"], sort=False).cumsum() - valid
    expected_pa = pa_win.groupby(ordered["match_id"], sort=False).cumsum() - pa_win
    expected_pb = pb_win.groupby(ordered["match_id"], sort=False).cumsum() - pb_win
    if not ordered["points_played_before"].astype("int64").equals(expected_valid_points.astype("int64")):
        errors.append("points_played_before does not equal prior valid point count")
    if not ordered["player_a_points_won_before"].astype("int64").equals(expected_pa.astype("int64")):
        errors.append("player_a_points_won_before includes current/future outcome or misses prior outcome")
    if not ordered["player_b_points_won_before"].astype("int64").equals(expected_pb.astype("int64")):
        errors.append("player_b_points_won_before includes current/future outcome or misses prior outcome")
    if int((expected_points < ordered["points_played_before"]).sum()):
        errors.append("points_played_before exceeds raw prior row count")

    expected_recent_a_5 = ordered.assign(_pa=pa_win, _valid=valid).groupby("match_id", sort=False).apply(
        lambda g: rolling_prior_pct(g["_pa"], g["_valid"], 5)
    ).reset_index(level=0, drop=True)
    diff = (ordered["player_a_recent_5_win_pct_before"].astype(float) - expected_recent_a_5.astype(float)).abs().fillna(0)
    if bool((diff > 1e-9).any()):
        errors.append("player_a_recent_5_win_pct_before is not based only on prior events")


def validate_baselines(baselines: pd.DataFrame, errors: List[str]) -> None:
    if baselines.empty:
        errors.append("player baseline dataset is empty")
        return
    for col in PLAYER_BASELINE_COLUMNS:
        if col not in baselines.columns:
            errors.append(f"player baseline missing column: {col}")
    allowed = {"strong", "moderate", "weak", "invalid_or_placeholder"}
    bad_levels = sorted(set(baselines["baseline_quality_level"].dropna()) - allowed)
    if bad_levels:
        errors.append(f"unknown baseline quality levels: {bad_levels}")
    if ((baselines["is_unknown_placeholder"]) & (baselines["baseline_quality_level"] == "strong")).any():
        errors.append("unknown placeholders are treated as strong baselines")
    bounded_cols = ["serve_points", "serve_points_won", "return_points", "return_points_won", "aces", "double_faults"]
    for col in bounded_cols:
        if (baselines[col] < 0).any():
            errors.append(f"baseline column contains negative values: {col}")
    if (baselines["serve_points_won"] > baselines["serve_points"]).any():
        errors.append("serve_points_won exceeds serve_points")
    if (baselines["return_points_won"] > baselines["return_points"]).any():
        errors.append("return_points_won exceeds return_points")


def validate_replay(replay: pd.DataFrame, errors: List[str]) -> None:
    if replay.empty:
        errors.append("replay manifest is empty")
        return
    for col in REPLAY_COLUMNS:
        if col not in replay.columns:
            errors.append(f"replay manifest missing column: {col}")
    if replay["synthetic_event_id"].duplicated().any():
        errors.append("synthetic_event_id is not unique")
    expected_match = replay["source_match_id"].map(lambda x: stable_id("synthetic_match", x, 42))
    if not replay["synthetic_match_id"].astype(str).equals(expected_match.astype(str)):
        errors.append("synthetic_match_id is not deterministic under seed 42")
    expected_event = [
        stable_id("synthetic_event", row.synthetic_match_id, row.event_id, row.event_index, 42, length=24)
        for row in replay[["synthetic_match_id", "event_id", "event_index"]].itertuples(index=False)
    ]
    if replay["synthetic_event_id"].tolist() != expected_event:
        errors.append("synthetic_event_id is not deterministic under seed 42")
    for mid, group in replay.groupby("synthetic_match_id", sort=False):
        if not group["replay_order"].is_monotonic_increasing:
            errors.append(f"replay_order is not monotonic for {mid}")
            break
        if not group["replay_offset_seconds"].is_monotonic_increasing:
            errors.append(f"replay_offset_seconds is not monotonic for {mid}")
            break


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--curated", type=Path, default=Path("data/curated"))
    parser.add_argument("--features", type=Path, default=Path("data/features"))
    parser.add_argument("--baselines", type=Path, default=Path("data/baselines"))
    parser.add_argument("--replay", type=Path, default=Path("data/replay"))
    parser.add_argument("--contracts", type=Path, default=Path("contracts"))
    args = parser.parse_args()

    errors: List[str] = []
    curated = read_parquet_dir(args.curated / "singles_points")
    point_features = read_parquet_dir(args.features / "point_features")
    match_features = read_parquet_dir(args.features / "match_features")
    baselines = read_parquet_dir(args.baselines / "player_baselines")
    replay_manifest_path = args.replay / "manifests" / "replay_manifest_v1.parquet"
    replay = pd.read_parquet(replay_manifest_path, engine="pyarrow") if replay_manifest_path.exists() else pd.DataFrame()

    for path in [
        args.features / "point_features",
        args.features / "match_features",
        args.baselines / "player_baselines",
    ]:
        if not sorted(path.glob("part-*.parquet")):
            errors.append(f"missing Parquet parts under {path}")
    require_file(replay_manifest_path, errors)
    for path in [
        args.features / "feature_build_report.json",
        args.features / "feature_quality_report.json",
        args.baselines / "baseline_quality_report.json",
        args.replay / "replay_manifest_report.json",
        args.replay / "manifests" / "replay_manifest_v1.json",
        args.features / "zone_metadata.json",
        args.baselines / "zone_metadata.json",
        args.replay / "zone_metadata.json",
        args.contracts / "point_feature_schema.json",
        args.contracts / "match_feature_schema.json",
        args.contracts / "player_baseline_schema.json",
        args.contracts / "replay_manifest_schema.json",
        Path("docs/feature_engineering_audit.md"),
        Path("docs/baseline_generation_audit.md"),
        Path("docs/replay_manifest_audit.md"),
        Path("docs/next_implementation_steps.md"),
    ]:
        require_file(path, errors)
    if match_features.empty:
        errors.append("match feature dataset is empty")

    validate_point_features(curated, point_features, errors)
    validate_baselines(baselines, errors)
    validate_replay(replay, errors)

    result = {
        "generated_at": now_iso(),
        "status": "PASSED" if not errors else "FAILED",
        "blocking_errors": errors,
        "point_feature_rows": int(len(point_features)),
        "curated_point_rows": int(len(curated)),
        "match_feature_rows": int(len(match_features)),
        "baseline_rows": int(len(baselines)),
        "replay_manifest_rows": int(len(replay)),
    }
    write_json(args.features / "validation_report.json", result)
    Path("docs").mkdir(parents=True, exist_ok=True)
    next_steps_path = Path("docs/next_implementation_steps.md")
    if not next_steps_path.exists():
        blockers_text = (
            "\n".join(f"- {error}" for error in errors)
            if errors
            else "- Surface-specific features and baselines remain blocked until metadata improves.\n"
            "- Rally-length features remain sparse and should not be primary MVP model inputs.\n"
            "- ATP match bridge features remain blocked until a reliable point-to-match join is validated."
        )
        next_steps_path.write_text(
            f"""# Next Implementation Steps

Milestone 2A status: **{result['status']}**.

## Proceed To Model Training

{"Yes. The point-in-time-safe feature layer, player baselines, replay manifest, reports, contracts, and validation checks are present." if result["status"] == "PASSED" else "No. Resolve the listed Milestone 2A validation blockers before model training."}

## Proceed To Replay Producer

{"Yes, but only as the next implementation milestone. Kafka was not started here; `data/replay/manifests/replay_manifest_v1.parquet` is ready for a producer to consume." if result["status"] == "PASSED" else "No. Resolve replay manifest validation blockers first."}

## Blockers

{blockers_text}

## Exact Next Milestone Recommendation

Proceed to **Milestone 2B: model training and model artifact publication** after reviewing the generated feature quality report. Kafka replay producer work can follow from the prepared manifest, but should not replace model-training validation.
""",
            encoding="utf-8",
        )
    if errors:
        raise SystemExit(json.dumps(result, indent=2, sort_keys=True))
    print(
        "Milestone 2A PASSED: "
        f"point_features={len(point_features)} match_features={len(match_features)} "
        f"baselines={len(baselines)} replay_events={len(replay)}"
    )


if __name__ == "__main__":
    main()
