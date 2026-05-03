#!/usr/bin/env python3
"""Publish staged Milestone 2.7 model artifacts after validation gates pass."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd

from model_artifact_lib import (
    copytree_replace,
    feature_schema_hash,
    is_finite_probability,
    now_iso,
    read_json,
    score_odds_dataframe,
    score_risk_row,
    write_json,
)


def publish_odds(models: Path, version: str) -> None:
    staging = models / "odds" / "staging"
    target = models / "odds" / version
    metadata = read_json(staging / "metadata.json")
    feature_schema = read_json(staging / "feature_schema.json")
    eval_report = read_json(staging / "eval_report.json")
    expected_hash = feature_schema_hash(feature_schema["feature_columns"], feature_schema["target_column"])
    failures = []
    if metadata["feature_schema_hash"] != expected_hash or feature_schema["feature_schema_hash"] != expected_hash:
        failures.append("feature schema hash mismatch")
    if eval_report.get("status") != "PASSED":
        failures.extend(eval_report.get("blocking_errors", ["odds eval report did not pass"]))
    model = joblib.load(staging / "model.joblib")
    fixture = pd.read_parquet(staging / "validation_fixture.parquet").head(20)
    probabilities = score_odds_dataframe(model, fixture, feature_schema["feature_columns"])
    if not probabilities or not all(is_finite_probability(value) for value in probabilities):
        failures.append("fixture probabilities are not valid")
    if failures:
        write_json(staging / "publication_failure.json", {"published": False, "failure_reasons": failures})
        raise SystemExit("odds publication failed: " + "; ".join(failures))
    copytree_replace(staging, target)
    latest = {
        "schema_version": "model_registry_v1",
        "model_type": "odds",
        "version": version,
        "status": "published",
        "artifact_path": f"data/models/odds/{version}/model.joblib",
        "metadata_path": f"data/models/odds/{version}/metadata.json",
        "feature_schema_path": f"data/models/odds/{version}/feature_schema.json",
        "eval_report_path": f"data/models/odds/{version}/eval_report.json",
        "published_at": now_iso(),
        "feature_schema_hash": expected_hash,
        "validation_status": "passed",
        "limitations": metadata["limitations"],
    }
    write_json(models / "odds" / "latest.json", latest)
    print(f"Published odds model to {target}")


def publish_risk(models: Path, version: str) -> None:
    staging = models / "risk" / "staging"
    target = models / "risk" / version
    config = read_json(staging / "risk_config.json")
    metadata = read_json(staging / "metadata.json")
    eval_report = read_json(staging / "eval_report.json")
    failures = []
    if config.get("fake_labels_used") is not False or metadata.get("fake_labels_used") is not False:
        failures.append("risk artifact uses fake labels")
    if eval_report.get("status") != "PASSED":
        failures.extend(eval_report.get("blocking_errors", ["risk eval report did not pass"]))
    fixture = pd.read_parquet(staging / "validation_fixture.parquet").head(3)
    scores = [score_risk_row(row, config) for row in fixture.to_dict(orient="records")]
    if not scores or not all(0.0 <= score["risk_score"] <= 1.0 for score in scores):
        failures.append("risk fixture scoring failed")
    if failures:
        write_json(staging / "publication_failure.json", {"published": False, "failure_reasons": failures})
        raise SystemExit("risk publication failed: " + "; ".join(failures))
    copytree_replace(staging, target)
    config_hash = feature_schema_hash(config["features_used"], "risk_score")
    latest = {
        "schema_version": "model_registry_v1",
        "model_type": "risk",
        "version": version,
        "status": "published",
        "artifact_path": f"data/models/risk/{version}/risk_config.json",
        "metadata_path": f"data/models/risk/{version}/metadata.json",
        "feature_schema_path": f"data/models/risk/{version}/risk_config.json",
        "eval_report_path": f"data/models/risk/{version}/eval_report.json",
        "published_at": now_iso(),
        "feature_schema_hash": config_hash,
        "validation_status": "passed",
        "limitations": config["limitations"],
    }
    write_json(models / "risk" / "latest.json", latest)
    print(f"Published risk config to {target}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", type=Path, default=Path("data/models"))
    parser.add_argument("--model-type", choices=["odds", "risk"], required=True)
    parser.add_argument("--version", default="v1")
    args = parser.parse_args()
    if args.model_type == "odds":
        publish_odds(args.models, args.version)
    else:
        publish_risk(args.models, args.version)


if __name__ == "__main__":
    main()
