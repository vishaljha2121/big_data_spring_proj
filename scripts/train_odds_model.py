#!/usr/bin/env python3
"""Train Milestone 2.7 odds models and write staging artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from model_artifact_lib import (
    EXCLUDED_COLUMNS,
    ODDS_GATES,
    deterministic_match_split,
    feature_schema_hash,
    load_point_features,
    now_iso,
    score_odds_dataframe,
    selected_feature_columns,
    write_json,
    write_split_outputs,
)


def build_logistic(seed: int) -> Pipeline:
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "model",
                LogisticRegression(
                    max_iter=300,
                    solver="lbfgs",
                    random_state=seed,
                    class_weight="balanced",
                ),
            ),
        ]
    )


def build_hgb(seed: int) -> Pipeline:
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            (
                "model",
                HistGradientBoostingClassifier(
                    max_iter=120,
                    learning_rate=0.06,
                    max_leaf_nodes=31,
                    random_state=seed,
                ),
            ),
        ]
    )


def evaluate(model: Pipeline, df: pd.DataFrame, feature_columns: List[str], target: str) -> Dict[str, float]:
    y = pd.to_numeric(df[target], errors="coerce").astype(int)
    prob = model.predict_proba(df[feature_columns])[:, 1]
    return {
        "auc": float(roc_auc_score(y, prob)),
        "brier_score": float(brier_score_loss(y, prob)),
        "log_loss": float(log_loss(y, prob, labels=[0, 1])),
    }


def sample_training_rows(df: pd.DataFrame, max_train_rows: int | None, seed: int) -> pd.DataFrame:
    if max_train_rows is None or len(df) <= max_train_rows:
        return df
    return df.sample(n=max_train_rows, random_state=seed)


def train_candidates(
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_columns: List[str],
    target: str,
    seed: int,
) -> Tuple[str, Pipeline, Dict[str, Dict[str, float]]]:
    candidates = {
        "logistic_regression": build_logistic(seed),
        "hist_gradient_boosting": build_hgb(seed),
    }
    results: Dict[str, Dict[str, float]] = {}
    best_name = ""
    best_model: Pipeline | None = None
    best_auc = -1.0
    for name, model in candidates.items():
        model.fit(train_df[feature_columns], pd.to_numeric(train_df[target], errors="coerce").astype(int))
        validation_metrics = evaluate(model, validation_df, feature_columns, target)
        test_metrics = evaluate(model, test_df, feature_columns, target)
        results[name] = {
            "validation_auc": validation_metrics["auc"],
            "validation_brier_score": validation_metrics["brier_score"],
            "validation_log_loss": validation_metrics["log_loss"],
            "test_auc": test_metrics["auc"],
            "test_brier_score": test_metrics["brier_score"],
            "test_log_loss": test_metrics["log_loss"],
        }
        if validation_metrics["auc"] > best_auc:
            best_auc = validation_metrics["auc"]
            best_name = name
            best_model = model
    assert best_model is not None
    return best_name, best_model, results


def gates_pass(metrics: Dict[str, float]) -> Tuple[bool, List[str]]:
    failures = []
    if metrics["validation_auc"] < ODDS_GATES["validation_auc_min"]:
        failures.append("validation AUC below 0.55")
    if metrics["test_auc"] < ODDS_GATES["test_auc_min"]:
        failures.append("test AUC below 0.55")
    if metrics["validation_brier_score"] > ODDS_GATES["validation_brier_max"]:
        failures.append("validation Brier score above 0.30")
    if metrics["test_brier_score"] > ODDS_GATES["test_brier_max"]:
        failures.append("test Brier score above 0.30")
    return not failures, failures


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, default=Path("data/features"))
    parser.add_argument("--models", type=Path, default=Path("data/models"))
    parser.add_argument("--results", type=Path, default=Path("data/results/model_eval"))
    parser.add_argument("--target", default="label_point_winner_is_player_a")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-train-rows", type=int, default=300000)
    parser.add_argument("--max-eval-rows", type=int, default=300000)
    args = parser.parse_args()

    required = set(EXCLUDED_COLUMNS + [args.target, "match_id"] + selected_feature_columns(pd.DataFrame(columns=[])))
    df = load_point_features(args.features)
    feature_columns = selected_feature_columns(df)
    if args.target not in df.columns:
        raise SystemExit(f"missing target column: {args.target}")
    df = df.dropna(subset=["match_id", args.target]).copy()
    df[args.target] = pd.to_numeric(df[args.target], errors="coerce")
    df = df[df[args.target].isin([0, 1])]

    splits, split_report = deterministic_match_split(df, args.seed, args.target)
    write_split_outputs(args.models, splits, split_report)
    split_sets = {name: set(values) for name, values in splits.items()}
    train_df_full = df[df["match_id"].isin(split_sets["train"])]
    validation_df_full = df[df["match_id"].isin(split_sets["validation"])]
    test_df_full = df[df["match_id"].isin(split_sets["test"])]
    train_df = sample_training_rows(train_df_full, args.max_train_rows, args.seed)
    validation_df = sample_training_rows(validation_df_full, args.max_eval_rows, args.seed + 1)
    test_df = sample_training_rows(test_df_full, args.max_eval_rows, args.seed + 2)

    selected_name, selected_model, candidate_metrics = train_candidates(
        train_df=train_df,
        validation_df=validation_df,
        test_df=test_df,
        feature_columns=feature_columns,
        target=args.target,
        seed=args.seed,
    )
    selected_metrics = candidate_metrics[selected_name]
    passed, gate_failures = gates_pass(selected_metrics)
    schema_hash = feature_schema_hash(feature_columns, args.target)

    staging = args.models / "odds" / "staging"
    staging.mkdir(parents=True, exist_ok=True)
    args.results.mkdir(parents=True, exist_ok=True)
    joblib.dump(selected_model, staging / "model.joblib")

    feature_schema = {
        "schema_version": "odds_model_feature_schema_v1",
        "feature_schema_hash": schema_hash,
        "feature_columns": feature_columns,
        "excluded_columns": sorted(set(EXCLUDED_COLUMNS)),
        "target_column": args.target,
        "null_handling": "sklearn SimpleImputer(strategy='median') inside the published pipeline",
        "leakage_guards": [
            "match-level train/validation/test split",
            "future outcome labels excluded from feature_columns",
            "event_id, match_id, source_file, schema_version, and raw player names excluded",
            "rally and surface features excluded from the MVP model",
        ],
    }
    metadata = {
        "schema_version": "odds_model_metadata_v1",
        "model_type": "odds",
        "version": "v1",
        "trained_at": now_iso(),
        "training_script": "scripts/train_odds_model.py",
        "target_column": args.target,
        "feature_columns": feature_columns,
        "excluded_columns": sorted(set(EXCLUDED_COLUMNS)),
        "feature_schema_hash": schema_hash,
        "input_dataset": "data/features/point_features",
        "train_row_count": int(len(train_df)),
        "validation_row_count": int(len(validation_df)),
        "test_row_count": int(len(test_df)),
        "validation_auc": selected_metrics["validation_auc"],
        "test_auc": selected_metrics["test_auc"],
        "validation_brier_score": selected_metrics["validation_brier_score"],
        "test_brier_score": selected_metrics["test_brier_score"],
        "random_seed": args.seed,
        "limitations": [
            "Surface features excluded because surface coverage is unavailable.",
            "Rally-length features excluded from the primary MVP model because coverage is sparse.",
            "ATP-derived labels/features excluded because no reliable bridge is validated.",
        ],
    }
    eval_report = {
        "schema_version": "model_eval_report_v1",
        "model_type": "odds",
        "generated_at": metadata["trained_at"],
        "status": "PASSED" if passed else "FAILED",
        "metrics": {
            "version": "v1",
            "target_column": args.target,
            "selected_model_type": selected_name,
            "candidate_metrics": candidate_metrics,
            "feature_count": len(feature_columns),
        },
        "quality_gates": ODDS_GATES,
        "blocking_errors": gate_failures,
        "warnings": [],
    }
    validation_fixture = validation_df.head(1000).copy()
    predictions = score_odds_dataframe(selected_model, validation_fixture, feature_columns)
    validation_fixture.to_parquet(staging / "validation_fixture.parquet", index=False)
    write_json(staging / "validation_predictions.json", {"predictions": predictions[:1000]})
    write_json(staging / "metadata.json", metadata)
    write_json(staging / "feature_schema.json", feature_schema)
    write_json(staging / "eval_report.json", eval_report)
    write_json(args.results / "odds_model_eval_report.json", eval_report)
    calibration = {
        "schema_version": "calibration_summary_v1",
        "model_type": "odds",
        "selected_model_type": selected_name,
        "validation_brier_score": selected_metrics["validation_brier_score"],
        "test_brier_score": selected_metrics["test_brier_score"],
    }
    write_json(args.results / "calibration_summary.json", calibration)
    model_step = selected_model.named_steps.get("model")
    importance: Dict[str, Any] = {"model_type": selected_name, "feature_columns": feature_columns}
    if hasattr(model_step, "coef_"):
        importance["coefficients"] = [float(v) for v in np.ravel(model_step.coef_)]
    elif hasattr(model_step, "feature_importances_"):
        importance["feature_importances"] = [float(v) for v in model_step.feature_importances_]
    else:
        importance["feature_importance_note"] = "selected model does not expose native coefficients"
    write_json(args.results / "feature_importance_or_coefficients.json", importance)
    print(f"Trained odds model: selected={selected_name} validation_auc={selected_metrics['validation_auc']:.4f} test_auc={selected_metrics['test_auc']:.4f}")


if __name__ == "__main__":
    main()
