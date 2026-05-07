"""Load published odds and risk artifacts for runtime scoring."""

from __future__ import annotations

import hashlib
import json
import warnings
from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_feature_hash(feature_columns: List[str], target_column: str) -> str:
    payload = {"feature_columns": feature_columns, "target_column": target_column}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class OddsModelLoader:
    def __init__(self, latest_path: Path):
        self.latest_path = latest_path
        self.latest = read_json(latest_path)
        root = Path.cwd()
        self.model = joblib.load(root / self.latest["artifact_path"])
        self.feature_schema = read_json(root / self.latest["feature_schema_path"])
        self.metadata = read_json(root / self.latest["metadata_path"])
        self.feature_columns = list(self.feature_schema["feature_columns"])
        self.feature_schema_hash = self.feature_schema["feature_schema_hash"]
        self.target_column = self.feature_schema["target_column"]
        expected = stable_feature_hash(self.feature_columns, self.target_column)
        if self.feature_schema_hash != expected or self.metadata["feature_schema_hash"] != expected:
            raise ValueError("odds feature schema hash mismatch")
        if self.latest["feature_schema_hash"] != expected:
            raise ValueError("odds latest.json feature schema hash mismatch")
        self.version = self.latest["version"]
        self.selected_model_type = read_json(root / self.latest["eval_report_path"])["metrics"]["selected_model_type"]

    def validate_features(self, features_df: pd.DataFrame) -> None:
        missing = [col for col in self.feature_columns if col not in features_df.columns]
        if missing:
            raise ValueError(f"missing required odds feature columns: {missing}")

    def predict_proba(self, features_df: pd.DataFrame) -> List[float]:
        self.validate_features(features_df)
        frame = features_df[self.feature_columns].apply(pd.to_numeric, errors="coerce").astype(float)
        probabilities = self.model.predict_proba(frame)[:, 1]
        output = [float(value) for value in probabilities]
        if any(value < 0.0 or value > 1.0 for value in output):
            raise ValueError("odds probabilities outside [0, 1]")
        return output

    def predict_one(self, feature_row: Dict[str, Any]) -> float:
        missing = [col for col in self.feature_columns if col not in feature_row]
        if missing:
            raise ValueError(f"missing required odds feature columns: {missing}")
        row = np.array([[feature_row[col] for col in self.feature_columns]], dtype=float)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="X does not have valid feature names")
            probability = float(self.model.predict_proba(row)[:, 1][0])
        if probability < 0.0 or probability > 1.0:
            raise ValueError("odds probability outside [0, 1]")
        return probability


class OutcomeModelLoader:
    def __init__(self, latest_path: Path):
        self.latest_path = latest_path
        self.latest = read_json(latest_path)
        root = Path.cwd()
        self.model = joblib.load(root / self.latest["path"] / "model.joblib")
        self.feature_schema = read_json(root / self.latest["path"] / "feature_schema.json")
        self.metadata = read_json(root / self.latest["path"] / "metadata.json")
        self.feature_columns = list(self.feature_schema["feature_columns"])
        self.target_column = self.feature_schema["target_column"]
        self.version = self.latest["latest_version"]
        self.model_type = self.latest["model_type"]

    def validate_features(self, features_df: pd.DataFrame) -> None:
        missing = [col for col in self.feature_columns if col not in features_df.columns]
        if missing:
            raise ValueError(f"missing required {self.model_type} feature columns: {missing}")

    def predict_one(self, feature_row: Dict[str, Any]) -> float:
        missing = [col for col in self.feature_columns if col not in feature_row]
        if missing:
            raise ValueError(f"missing required {self.model_type} feature columns: {missing}")
        row = np.array([[feature_row[col] for col in self.feature_columns]], dtype=float)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="X does not have valid feature names")
            probability = float(self.model.predict_proba(row)[:, 1][0])
        return probability



class RiskConfigLoader:
    def __init__(self, latest_path: Path):
        self.latest_path = latest_path
        self.latest = read_json(latest_path)
        root = Path.cwd()
        self.config = read_json(root / self.latest["artifact_path"])
        self.metadata = read_json(root / self.latest["metadata_path"])
        if self.config.get("fake_labels_used") is not False:
            raise ValueError("risk config must not use fake labels")
        self.version = self.latest["version"]
        self.features_used = list(self.config["features_used"])
