#!/usr/bin/env python3
"""Validate published Milestone 2.7 model artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import joblib
import jsonschema
import pandas as pd

from model_artifact_lib import (
    ODDS_GATES,
    feature_schema_hash,
    is_finite_probability,
    read_json,
    score_odds_dataframe,
    score_risk_row,
    write_json,
)


def validate_json(payload_path: Path, schema_path: Path, errors: List[str]) -> None:
    try:
        jsonschema.validate(read_json(payload_path), read_json(schema_path))
    except Exception as exc:
        errors.append(f"{payload_path} does not validate against {schema_path}: {exc}")


def validate_split(models: Path, errors: List[str]) -> None:
    split_dir = models / "splits"
    train = set(read_json(split_dir / "train_match_ids.json")["match_ids"])
    validation = set(read_json(split_dir / "validation_match_ids.json")["match_ids"])
    test = set(read_json(split_dir / "test_match_ids.json")["match_ids"])
    if not train or not validation or not test:
        errors.append("one or more split files are empty")
    if not (train.isdisjoint(validation) and train.isdisjoint(test) and validation.isdisjoint(test)):
        errors.append("match_id leakage detected across train/validation/test splits")
    report = read_json(split_dir / "split_report.json")
    if report.get("leakage_check_passed") is not True:
        errors.append("split_report leakage_check_passed is not true")


def validate_odds(models: Path, contracts: Path, errors: List[str]) -> None:
    odds = models / "odds" / "v1"
    required = ["model.joblib", "metadata.json", "feature_schema.json", "eval_report.json", "validation_fixture.parquet", "validation_predictions.json"]
    for name in required:
        if not (odds / name).exists():
            errors.append(f"missing odds artifact: {odds / name}")
    if not (models / "odds" / "latest.json").exists():
        errors.append("missing odds latest.json")
        return
    validate_json(odds / "metadata.json", contracts / "odds_model_metadata_schema.json", errors)
    validate_json(odds / "feature_schema.json", contracts / "odds_model_feature_schema.json", errors)
    validate_json(odds / "eval_report.json", contracts / "model_eval_report_schema.json", errors)
    validate_json(models / "odds" / "latest.json", contracts / "model_registry_schema.json", errors)
    metadata = read_json(odds / "metadata.json")
    feature_schema = read_json(odds / "feature_schema.json")
    expected_hash = feature_schema_hash(feature_schema["feature_columns"], feature_schema["target_column"])
    if metadata["feature_schema_hash"] != expected_hash or feature_schema["feature_schema_hash"] != expected_hash:
        errors.append("odds feature_schema_hash mismatch")
    if metadata["validation_auc"] < ODDS_GATES["validation_auc_min"]:
        errors.append("odds validation AUC gate failed")
    if metadata["test_auc"] < ODDS_GATES["test_auc_min"]:
        errors.append("odds test AUC gate failed")
    if metadata["validation_brier_score"] > ODDS_GATES["validation_brier_max"]:
        errors.append("odds validation Brier gate failed")
    if metadata["test_brier_score"] > ODDS_GATES["test_brier_max"]:
        errors.append("odds test Brier gate failed")
    model = joblib.load(odds / "model.joblib")
    fixture = pd.read_parquet(odds / "validation_fixture.parquet").head(25)
    probabilities = score_odds_dataframe(model, fixture, feature_schema["feature_columns"])
    if not probabilities or not all(is_finite_probability(value) for value in probabilities):
        errors.append("odds fixture scoring produced invalid probabilities")


def validate_risk(models: Path, contracts: Path, errors: List[str]) -> None:
    risk = models / "risk" / "v1"
    required = ["risk_config.json", "metadata.json", "eval_report.json", "validation_fixture.parquet", "validation_scores.json"]
    for name in required:
        if not (risk / name).exists():
            errors.append(f"missing risk artifact: {risk / name}")
    if not (models / "risk" / "latest.json").exists():
        errors.append("missing risk latest.json")
        return
    validate_json(risk / "risk_config.json", contracts / "risk_config_schema.json", errors)
    validate_json(risk / "metadata.json", contracts / "risk_model_metadata_schema.json", errors)
    validate_json(risk / "eval_report.json", contracts / "model_eval_report_schema.json", errors)
    validate_json(models / "risk" / "latest.json", contracts / "model_registry_schema.json", errors)
    config = read_json(risk / "risk_config.json")
    if config.get("fake_labels_used") is not False:
        errors.append("risk fake_labels_used is not false")
    fixture = pd.read_parquet(risk / "validation_fixture.parquet").head(5)
    scores = [score_risk_row(row, config) for row in fixture.to_dict(orient="records")]
    if not scores or any(score["risk_bucket"] not in {"low", "medium", "high"} for score in scores):
        errors.append("risk fixture scoring failed")
    if any(not (0.0 <= score["risk_score"] <= 1.0) for score in scores):
        errors.append("risk score outside [0, 1]")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", type=Path, default=Path("data/models"))
    parser.add_argument("--contracts", type=Path, default=Path("contracts"))
    parser.add_argument("--results", type=Path, default=Path("data/results/model_eval"))
    args = parser.parse_args()
    errors: List[str] = []
    validate_split(args.models, errors)
    validate_odds(args.models, args.contracts, errors)
    validate_risk(args.models, args.contracts, errors)
    for name in ["odds_model_eval_report.json", "risk_model_eval_report.json", "calibration_summary.json", "feature_importance_or_coefficients.json"]:
        if not (args.results / name).exists():
            errors.append(f"missing model eval result: {args.results / name}")
    report = {
        "status": "PASSED" if not errors else "FAILED",
        "blocking_errors": errors,
    }
    write_json(args.results / "model_artifact_validation_report.json", report)
    if errors:
        raise SystemExit(json.dumps(report, indent=2))
    print("Milestone 2.7 model artifacts PASSED validation")


if __name__ == "__main__":
    main()
