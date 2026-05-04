"""End-to-end event scorer for replay JSONL/Kafka point events."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import jsonschema
from streaming.model_loader import OddsModelLoader, RiskConfigLoader
from streaming.online_feature_builder import OnlineFeatureBuilder
from streaming.risk_scorer import RuntimeRiskScorer
from streaming.scored_event_schema import SCORED_EVENT_SCHEMA_VERSION, SCORER_VERSION


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class StreamScorer:
    def __init__(
        self,
        odds_latest: Path,
        risk_latest: Path,
        point_event_schema: Path = Path("contracts/point_event_schema.json"),
    ):
        self.odds = OddsModelLoader(odds_latest)
        self.risk_loader = RiskConfigLoader(risk_latest)
        self.risk = RuntimeRiskScorer(self.risk_loader.config)
        self.feature_builder = OnlineFeatureBuilder(self.odds.feature_columns)
        self.point_event_schema = json.loads(point_event_schema.read_text(encoding="utf-8"))
        self.point_event_validator = jsonschema.Draft7Validator(self.point_event_schema)
        self.defaulted_features = self.feature_builder.defaulted_features
        self.missing_features = self.feature_builder.missing_features

    def validate_event(self, event: Dict[str, Any]) -> None:
        self.point_event_validator.validate(event)

    def score_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        start = time.perf_counter()
        self.validate_event(event)
        features = self.feature_builder.build_features(event)
        probability_a = self.odds.predict_one(features)
        risk = self.risk.score(features)
        self.feature_builder.update_state(event)
        latency_ms = (time.perf_counter() - start) * 1000.0
        return self.format_scored_event(event, probability_a, risk, latency_ms)

    def format_scored_event(
        self,
        event: Dict[str, Any],
        probability_a: float,
        risk: Dict[str, Any],
        latency_ms: float,
    ) -> Dict[str, Any]:
        return {
            "schema_version": SCORED_EVENT_SCHEMA_VERSION,
            "scorer_version": SCORER_VERSION,
            "replay_session_id": event["replay_session_id"],
            "synthetic_match_id": event["synthetic_match_id"],
            "source_match_id": event["source_match_id"],
            "event_id": event["event_id"],
            "synthetic_event_id": event["synthetic_event_id"],
            "event_index": event["event_index"],
            "replay_order": event["replay_order"],
            "event_ts": event.get("event_ts"),
            "player_a": event["player_a"],
            "player_b": event["player_b"],
            "server_player": event.get("server_player"),
            "receiver_player": event.get("receiver_player"),
            "point_winner_player": event.get("point_winner_player"),
            "point_probability_player_a": float(probability_a),
            "point_probability_player_b": float(1.0 - probability_a),
            "selected_model_type": self.odds.selected_model_type,
            "odds_model_version": self.odds.version,
            "feature_schema_hash": self.odds.feature_schema_hash,
            "risk_score": risk["risk_score"],
            "risk_bucket": risk["risk_bucket"],
            "primary_risk_signal": risk["primary_signal"],
            "risk_explanation": risk["explanation"],
            "missing_feature_warnings": risk["missing_feature_warnings"],
            "scoring_latency_ms": float(latency_ms),
            "scored_at": now_iso(),
            "input_event_valid": True,
            "feature_row_valid": True,
        }
