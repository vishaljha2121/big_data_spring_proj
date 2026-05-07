#!/usr/bin/env python3
"""Train richer outcome models and write staging artifacts."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
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


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_COLUMNS = [
    "event_id", "match_id", "event_index", "player_a", "player_b",
    "server_player", "receiver_player", "point_winner_player", "source_file",
    "schema_version", "label_point_winner_is_player_a", "label_server_won_point",
    "label_match_winner_is_player_a", "label_match_winner_player",
    "label_player_a_wins_game", "label_player_a_wins_set", "label_player_a_wins_match"
]

OUTCOME_GATES = {
    "validation_auc_min": 0.55,
    "test_auc_min": 0.55,
    "validation_brier_max": 0.30,
    "test_brier_max": 0.30,
}

def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def build_logistic(seed: int) -> Pipeline:
    return Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(max_iter=300, solver="lbfgs", random_state=seed, class_weight="balanced")),
    ])

def build_hgb(seed: int) -> Pipeline:
    return Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("model", HistGradientBoostingClassifier(max_iter=100, learning_rate=0.08, max_leaf_nodes=31, random_state=seed)),
    ])

def evaluate(model: Pipeline, df: pd.DataFrame, feature_columns: List[str], target: str) -> Dict[str, float]:
    y = pd.to_numeric(df[target], errors="coerce").astype(int)
    prob = model.predict_proba(df[feature_columns])[:, 1]
    return {
        "auc": float(roc_auc_score(y, prob)),
        "brier_score": float(brier_score_loss(y, prob)),
        "log_loss": float(log_loss(y, prob, labels=[0, 1])),
    }

def deterministic_match_split(df: pd.DataFrame, seed: int, target: str) -> Tuple[Dict[str, List[str]], Dict[str, Any]]:
    # Simple deterministic split by hashing match_id
    match_ids = list(df["match_id"].dropna().unique())
    match_ids.sort()
    rng = np.random.RandomState(seed)
    rng.shuffle(match_ids)
    
    n = len(match_ids)
    n_train = int(n * 0.7)
    n_val = int(n * 0.15)
    
    splits = {
        "train": match_ids[:n_train],
        "validation": match_ids[n_train:n_train+n_val],
        "test": match_ids[n_train+n_val:]
    }
    
    report = {
        "generated_at": now_iso(),
        "total_matches": n,
        "train_matches": len(splits["train"]),
        "validation_matches": len(splits["validation"]),
        "test_matches": len(splits["test"]),
        "random_seed": seed,
    }
    return splits, report

def train_target(target_name: str, target_col: str, seed: int) -> None:
    data_path = ROOT / f"data/features/outcome_targets/point_to_{target_name}/part-00000.parquet"
    if not data_path.exists():
        print(f"Skipping {target_name}, data not found at {data_path}")
        return
        
    print(f"Training outcome model for {target_name}...")
    df = pd.read_parquet(data_path)
    
    numeric_bool_cols = df.select_dtypes(include=[np.number, bool]).columns.tolist()
    feature_columns = sorted([c for c in numeric_bool_cols if c not in EXCLUDED_COLUMNS + [target_col, "match_id"]])
    
    df[target_col] = pd.to_numeric(df[target_col], errors="coerce")
    df = df[df[target_col].isin([0, 1])]
    
    splits, _ = deterministic_match_split(df, seed, target_col)
    
    # We sample to speed up training
    train_df = df[df["match_id"].isin(splits["train"])].sample(n=min(200000, sum(df["match_id"].isin(splits["train"]))), random_state=seed)
    validation_df = df[df["match_id"].isin(splits["validation"])].sample(n=min(100000, sum(df["match_id"].isin(splits["validation"]))), random_state=seed+1)
    test_df = df[df["match_id"].isin(splits["test"])].sample(n=min(100000, sum(df["match_id"].isin(splits["test"]))), random_state=seed+2)

    candidates = {
        "logistic_regression": build_logistic(seed),
        "hist_gradient_boosting": build_hgb(seed),
    }
    
    best_auc = -1.0
    best_name = ""
    best_model = None
    candidate_metrics = {}
    
    for name, model in candidates.items():
        model.fit(train_df[feature_columns], train_df[target_col].astype(int))
        val_metrics = evaluate(model, validation_df, feature_columns, target_col)
        test_metrics = evaluate(model, test_df, feature_columns, target_col)
        
        candidate_metrics[name] = {
            "validation_auc": val_metrics["auc"],
            "validation_brier_score": val_metrics["brier_score"],
            "validation_log_loss": val_metrics["log_loss"],
            "test_auc": test_metrics["auc"],
            "test_brier_score": test_metrics["brier_score"],
            "test_log_loss": test_metrics["log_loss"],
        }
        if val_metrics["auc"] > best_auc:
            best_auc = val_metrics["auc"]
            best_name = name
            best_model = model

    selected_metrics = candidate_metrics[best_name]
    
    failures = []
    if selected_metrics["validation_auc"] < OUTCOME_GATES["validation_auc_min"]:
        failures.append("validation AUC below 0.55")
    if selected_metrics["test_auc"] < OUTCOME_GATES["test_auc_min"]:
        failures.append("test AUC below 0.55")
    if selected_metrics["validation_brier_score"] > OUTCOME_GATES["validation_brier_max"]:
        failures.append("validation Brier score above 0.30")
    if selected_metrics["test_brier_score"] > OUTCOME_GATES["test_brier_max"]:
        failures.append("test Brier score above 0.30")
        
    passed = len(failures) == 0

    staging = ROOT / f"data/models/outcomes/{target_name}/staging"
    staging.mkdir(parents=True, exist_ok=True)
    
    joblib.dump(best_model, staging / "model.joblib")
    
    metadata = {
        "schema_version": "outcome_model_metadata_v1",
        "model_type": f"outcome_{target_name}",
        "version": "v1",
        "trained_at": now_iso(),
        "training_script": "scripts/train_outcome_models.py",
        "target_column": target_col,
        "feature_columns": feature_columns,
        "input_dataset": str(data_path.relative_to(ROOT)),
        "validation_auc": selected_metrics["validation_auc"],
        "test_auc": selected_metrics["test_auc"],
        "validation_brier_score": selected_metrics["validation_brier_score"],
        "test_brier_score": selected_metrics["test_brier_score"],
        "random_seed": seed,
    }
    
    eval_report = {
        "schema_version": "outcome_model_eval_report_v1",
        "model_type": f"outcome_{target_name}",
        "generated_at": metadata["trained_at"],
        "status": "PASSED" if passed else "FAILED",
        "metrics": {
            "version": "v1",
            "target_column": target_col,
            "selected_model_type": best_name,
            "candidate_metrics": candidate_metrics,
            "feature_count": len(feature_columns),
        },
        "quality_gates": OUTCOME_GATES,
        "blocking_errors": failures,
        "warnings": [],
    }
    
    feature_schema = {
        "schema_version": "outcome_model_feature_schema_v1",
        "feature_columns": feature_columns,
        "target_column": target_col
    }
    
    validation_fixture = validation_df.head(1000).copy()
    predictions = best_model.predict_proba(validation_fixture[feature_columns])[:, 1].tolist()
    validation_fixture.to_parquet(staging / "validation_fixture.parquet", index=False)
    
    write_json(staging / "validation_predictions.json", {"predictions": predictions[:1000]})
    write_json(staging / "metadata.json", metadata)
    write_json(staging / "feature_schema.json", feature_schema)
    write_json(staging / "eval_report.json", eval_report)
    
    print(f"[{target_name.upper()}] Selected: {best_name} | Val AUC: {selected_metrics['validation_auc']:.4f} | Status: {'PASSED' if passed else 'FAILED'}")

def main() -> None:
    seed = 42
    targets = [
        ("game", "label_player_a_wins_game"),
        ("set", "label_player_a_wins_set"),
        ("match", "label_player_a_wins_match"),
    ]
    for name, col in targets:
        train_target(name, col, seed)

if __name__ == "__main__":
    main()
