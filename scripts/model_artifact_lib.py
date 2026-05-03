#!/usr/bin/env python3
"""Shared helpers for Milestone 2.7 model artifacts."""

from __future__ import annotations

import hashlib
import json
import math
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import joblib
import pandas as pd


ODDS_GATES = {
    "validation_auc_min": 0.55,
    "test_auc_min": 0.55,
    "validation_brier_max": 0.30,
    "test_brier_max": 0.30,
}

SAFE_ODDS_FEATURES = [
    "points_played_before",
    "player_a_points_won_before",
    "player_b_points_won_before",
    "player_a_point_win_pct_before",
    "player_b_point_win_pct_before",
    "server_points_played_before",
    "server_points_won_before",
    "server_point_win_pct_before",
    "receiver_points_played_before",
    "receiver_points_won_before",
    "receiver_point_win_pct_before",
    "player_a_recent_5_win_pct_before",
    "player_b_recent_5_win_pct_before",
    "player_a_recent_10_win_pct_before",
    "player_b_recent_10_win_pct_before",
    "player_a_aces_before",
    "player_b_aces_before",
    "player_a_double_faults_before",
    "player_b_double_faults_before",
    "elapsed_seconds_before",
    "elapsed_seconds_delta_from_prev",
    "is_server_player_a",
    "is_receiver_player_a",
    "has_valid_point_winner",
    "has_valid_server",
    "has_elapsed_seconds",
]

EXCLUDED_COLUMNS = [
    "event_id",
    "match_id",
    "event_index",
    "player_a",
    "player_b",
    "server_player",
    "receiver_player",
    "point_winner_player",
    "source_file",
    "schema_version",
    "elapsed_seconds",
    "set_number",
    "game_number",
    "point_number",
    "p1_score",
    "p2_score",
    "has_surface",
    "has_rally_length",
    "rally_length_avg_before",
    "player_a_rally_length_avg_before",
    "player_b_rally_length_avg_before",
    "label_point_winner_is_player_a",
    "label_server_won_point",
    "label_match_winner_is_player_a",
    "label_match_winner_player",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stable_hash(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def feature_schema_hash(feature_columns: List[str], target_column: str) -> str:
    return stable_hash({"feature_columns": feature_columns, "target_column": target_column})


def load_point_features(features_dir: Path, columns: Iterable[str] | None = None) -> pd.DataFrame:
    return pd.read_parquet(features_dir / "point_features", columns=list(columns) if columns else None)


def selected_feature_columns(df: pd.DataFrame) -> List[str]:
    return [col for col in SAFE_ODDS_FEATURES if col in df.columns]


def deterministic_match_split(df: pd.DataFrame, seed: int, target: str) -> Tuple[Dict[str, List[str]], Dict[str, Any]]:
    match_ids = pd.Series(df["match_id"].dropna().unique()).sort_values().sample(frac=1.0, random_state=seed).tolist()
    n = len(match_ids)
    train_end = int(n * 0.70)
    validation_end = int(n * 0.85)
    splits = {
        "train": match_ids[:train_end],
        "validation": match_ids[train_end:validation_end],
        "test": match_ids[validation_end:],
    }
    split_sets = {name: set(values) for name, values in splits.items()}
    leakage_passed = (
        split_sets["train"].isdisjoint(split_sets["validation"])
        and split_sets["train"].isdisjoint(split_sets["test"])
        and split_sets["validation"].isdisjoint(split_sets["test"])
    )
    report: Dict[str, Any] = {
        "seed": seed,
        "train_match_count": len(splits["train"]),
        "validation_match_count": len(splits["validation"]),
        "test_match_count": len(splits["test"]),
        "leakage_check_passed": leakage_passed,
        "target_column": target,
        "target_distributions": {},
    }
    for name, values in split_sets.items():
        split_df = df[df["match_id"].isin(values)]
        report[f"{name}_row_count"] = int(len(split_df))
        target_series = pd.to_numeric(split_df[target], errors="coerce").dropna()
        report["target_distributions"][name] = {
            "rows": int(len(target_series)),
            "positive_rate": float(target_series.mean()) if len(target_series) else None,
            "positive_count": int(target_series.sum()) if len(target_series) else 0,
            "negative_count": int((1 - target_series).sum()) if len(target_series) else 0,
        }
    return splits, report


def write_split_outputs(models_dir: Path, splits: Dict[str, List[str]], report: Dict[str, Any]) -> None:
    split_dir = models_dir / "splits"
    write_json(split_dir / "train_match_ids.json", {"match_ids": splits["train"]})
    write_json(split_dir / "validation_match_ids.json", {"match_ids": splits["validation"]})
    write_json(split_dir / "test_match_ids.json", {"match_ids": splits["test"]})
    write_json(split_dir / "split_report.json", report)


def copytree_replace(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def load_odds_artifact(model_dir: Path) -> Tuple[Any, Dict[str, Any], Dict[str, Any]]:
    model = joblib.load(model_dir / "model.joblib")
    metadata = read_json(model_dir / "metadata.json")
    feature_schema = read_json(model_dir / "feature_schema.json")
    return model, metadata, feature_schema


def score_odds_dataframe(model: Any, df: pd.DataFrame, feature_columns: List[str]) -> List[float]:
    missing = [col for col in feature_columns if col not in df.columns]
    if missing:
        raise ValueError(f"inference input missing feature columns: {missing}")
    probabilities = model.predict_proba(df[feature_columns])[:, 1]
    return [float(value) for value in probabilities]


def bucket_risk(score: float) -> str:
    if score < 0.40:
        return "low"
    if score < 0.70:
        return "medium"
    return "high"


def score_risk_row(row: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    warnings: List[str] = []
    deviations: List[Tuple[str, float]] = []
    baseline_expectations = config.get("baseline_expectations", {})
    for feature in config.get("features_used", []):
        current = row.get(feature)
        expected = baseline_expectations.get(feature)
        if current is None or expected is None:
            warnings.append(f"missing {feature} or baseline")
            continue
        try:
            current_f = float(current)
            expected_f = float(expected)
        except (TypeError, ValueError):
            warnings.append(f"non-numeric {feature}")
            continue
        deviations.append((feature, min(1.0, abs(current_f - expected_f))))

    if deviations:
        risk_score = max(0.0, min(1.0, sum(value for _, value in deviations) / len(deviations)))
        primary_signal = max(deviations, key=lambda item: item[1])[0]
    else:
        risk_score = 0.0
        primary_signal = "insufficient_baseline"
    bucket = bucket_risk(risk_score)
    template = config["explanation_templates"][bucket]
    return {
        "risk_score": float(risk_score),
        "risk_bucket": bucket,
        "primary_signal": primary_signal,
        "explanation": template.format(primary_signal=primary_signal, risk_score=round(risk_score, 4)),
        "missing_feature_warnings": warnings,
    }


def is_finite_probability(value: float) -> bool:
    return isinstance(value, (float, int)) and math.isfinite(value) and 0.0 <= float(value) <= 1.0
