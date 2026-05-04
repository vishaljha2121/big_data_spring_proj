"""File-backed data loading for the local serving layer."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from api.app.config import Settings, settings


def read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    records: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


class ApiDataStore:
    def __init__(self, cfg: Settings = settings):
        self.settings = cfg
        self.events = sorted(
            read_jsonl(cfg.scored_events_jsonl),
            key=lambda row: (row.get("synthetic_match_id", ""), row.get("replay_order", 0), row.get("event_id", "")),
        )
        self.event_by_id = {event["event_id"]: event for event in self.events}
        self.events_by_match: Dict[str, List[Dict[str, Any]]] = {}
        for event in self.events:
            self.events_by_match.setdefault(event["synthetic_match_id"], []).append(event)
        self.match_summaries = self._build_match_summaries()
        self.scoring_run_report = read_json(cfg.scoring_run_report) or {}
        self.scoring_validation_report = read_json(cfg.scoring_validation_report) or {}
        self.scoring_benchmark_report = read_json(cfg.scoring_benchmark_report) or {}
        self.odds_latest = read_json(cfg.odds_latest) or {}
        self.risk_latest = read_json(cfg.risk_latest) or {}
        root = cfg.scored_events_jsonl.parents[3]
        self.odds_metadata = read_json(root / self.odds_latest.get("metadata_path", "")) or {}
        self.odds_feature_schema = read_json(root / self.odds_latest.get("feature_schema_path", "")) or {}
        self.risk_metadata = read_json(root / self.risk_latest.get("metadata_path", "")) or {}
        self.risk_config = read_json(root / self.risk_latest.get("artifact_path", "")) or {}
        self.odds_eval_report = read_json(cfg.odds_eval_report) or {}
        self.risk_eval_report = read_json(cfg.risk_eval_report) or {}

    def readiness_checks(self) -> Dict[str, bool]:
        return {
            "scored_events_file": self.settings.scored_events_jsonl.exists(),
            "scoring_run_report": self.settings.scoring_run_report.exists(),
            "odds_latest": self.settings.odds_latest.exists(),
            "risk_latest": self.settings.risk_latest.exists(),
            "scored_events_loaded": bool(self.events),
        }

    def _build_match_summaries(self) -> List[Dict[str, Any]]:
        summaries: List[Dict[str, Any]] = []
        for match_id, events in self.events_by_match.items():
            risk_scores = [float(event.get("risk_score", 0.0)) for event in events]
            probabilities = [float(event.get("point_probability_player_a", 0.0)) for event in events]
            high_count = sum(1 for event in events if event.get("risk_bucket") == "high")
            summaries.append(
                {
                    "synthetic_match_id": match_id,
                    "source_match_id": events[0].get("source_match_id"),
                    "player_a": events[0].get("player_a"),
                    "player_b": events[0].get("player_b"),
                    "event_count": len(events),
                    "avg_point_probability_player_a": sum(probabilities) / len(probabilities) if probabilities else 0.0,
                    "max_risk_score": max(risk_scores) if risk_scores else 0.0,
                    "high_risk_event_count": high_count,
                    "first_event_ts": events[0].get("event_ts"),
                    "last_event_ts": events[-1].get("event_ts"),
                }
            )
        return sorted(summaries, key=lambda row: (-row["max_risk_score"], row["synthetic_match_id"]))


@lru_cache(maxsize=1)
def get_store() -> ApiDataStore:
    return ApiDataStore()
