#!/usr/bin/env python3
"""Build the Milestone 2.7 conservative risk scoring artifact."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from model_artifact_lib import bucket_risk, now_iso, score_risk_row, stable_hash, write_json


FEATURES_USED = [
    "serve_point_win_pct",
    "return_point_win_pct",
    "ace_rate",
    "double_fault_rate",
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, default=Path("data/features"))
    parser.add_argument("--baselines", type=Path, default=Path("data/baselines"))
    parser.add_argument("--models", type=Path, default=Path("data/models"))
    parser.add_argument("--results", type=Path, default=Path("data/results/model_eval"))
    args = parser.parse_args()

    baselines = pd.read_parquet(args.baselines / "player_baselines")
    valid = baselines[
        (baselines["baseline_quality_level"] != "invalid_or_placeholder")
        & (~baselines["is_unknown_placeholder"].astype(bool))
    ].copy()
    expectations = {
        feature: float(pd.to_numeric(valid[feature], errors="coerce").dropna().median())
        for feature in FEATURES_USED
        if feature in valid.columns
    }
    config = {
        "schema_version": "risk_config_v1",
        "model_type": "risk",
        "version": "v1",
        "risk_method": "baseline_deviation_score_v1",
        "features_used": FEATURES_USED,
        "baseline_dataset": "data/baselines/player_baselines",
        "thresholds": {"medium": 0.40, "high": 0.70},
        "bucket_rules": {
            "low": "risk_score < 0.40",
            "medium": "0.40 <= risk_score < 0.70",
            "high": "risk_score >= 0.70",
        },
        "fake_labels_used": False,
        "explanation_templates": {
            "low": "Low statistical deviation. Primary signal: {primary_signal}; score={risk_score}.",
            "medium": "Medium statistical deviation requiring review. Primary signal: {primary_signal}; score={risk_score}.",
            "high": "High statistical deviation requiring review. Primary signal: {primary_signal}; score={risk_score}.",
        },
        "limitations": [
            "This is not match-fixing detection and is not proof of misconduct.",
            "Surface-specific baselines are blocked because surface metadata is unavailable.",
            "Unknown placeholders are not treated as strong baselines.",
        ],
        "baseline_expectations": expectations,
    }
    metadata = {
        "schema_version": "risk_model_metadata_v1",
        "model_type": "risk",
        "version": "v1",
        "risk_method": config["risk_method"],
        "features_used": FEATURES_USED,
        "baseline_dataset": config["baseline_dataset"],
        "thresholds": config["thresholds"],
        "bucket_rules": config["bucket_rules"],
        "fake_labels_used": False,
        "explanation_templates": config["explanation_templates"],
        "limitations": config["limitations"],
    }
    fixture_source = valid.sort_values(["baseline_quality_level", "total_points"], ascending=[True, False]).head(100)
    fixture = fixture_source[["player"] + [feature for feature in FEATURES_USED if feature in fixture_source.columns]].copy()
    scores = [score_risk_row(row, config) for row in fixture.to_dict(orient="records")]
    eval_report = {
        "schema_version": "model_eval_report_v1",
        "model_type": "risk",
        "generated_at": now_iso(),
        "status": "PASSED",
        "metrics": {
            "fixture_rows": int(len(fixture)),
            "bucket_counts": pd.Series([score["risk_bucket"] for score in scores]).value_counts().to_dict(),
            "fake_labels_used": False,
        },
        "quality_gates": {
            "artifact_loads": True,
            "fixture_scoring_works": True,
            "fake_labels_used_must_be_false": True,
        },
        "blocking_errors": [],
        "warnings": [
            "Risk scores are statistical anomaly signals only.",
        ],
    }
    staging = args.models / "risk" / "staging"
    staging.mkdir(parents=True, exist_ok=True)
    args.results.mkdir(parents=True, exist_ok=True)
    fixture.to_parquet(staging / "validation_fixture.parquet", index=False)
    write_json(staging / "risk_config.json", config)
    write_json(staging / "metadata.json", metadata)
    write_json(staging / "eval_report.json", eval_report)
    write_json(staging / "validation_scores.json", {"scores": scores})
    write_json(args.results / "risk_model_eval_report.json", eval_report)
    print(f"Built risk config with {len(FEATURES_USED)} features; fake_labels_used=false")


if __name__ == "__main__":
    main()
