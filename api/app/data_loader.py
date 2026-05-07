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


def _load_replay_manifest(path: Path) -> List[Dict[str, Any]]:
    """Load replay manifest from parquet, returning list of dicts."""
    if not path.exists():
        return []
    try:
        import pyarrow.parquet as pq
        table = pq.read_table(path)
        return table.to_pylist()
    except ImportError:
        return []
    except Exception:
        return []


class ApiDataStore:
    def __init__(self, cfg: Settings = settings):
        self.settings = cfg

        # --- Scored events (existing) ----------------------------------
        self.events = sorted(
            read_jsonl(cfg.scored_events_jsonl),
            key=lambda row: (row.get("synthetic_match_id", ""), row.get("replay_order", 0), row.get("event_id", "")),
        )
        self.event_by_id = {event["event_id"]: event for event in self.events}
        self.events_by_match: Dict[str, List[Dict[str, Any]]] = {}
        for event in self.events:
            self.events_by_match.setdefault(event["synthetic_match_id"], []).append(event)
        self.match_summaries = self._build_match_summaries()

        # --- Replay manifest (new) ------------------------------------
        self._replay_events_raw = _load_replay_manifest(cfg.replay_manifest_parquet)
        self.replay_events_by_match: Dict[str, List[Dict[str, Any]]] = {}
        for evt in self._replay_events_raw:
            self.replay_events_by_match.setdefault(evt.get("synthetic_match_id", ""), []).append(evt)
        # Sort each match's events by replay_order
        for mid in self.replay_events_by_match:
            self.replay_events_by_match[mid].sort(key=lambda r: r.get("replay_order", 0))
        self.replay_manifest_report = read_json(cfg.replay_manifest_report) or {}
        self.replay_match_catalog = self._build_replay_match_catalog()

        # --- Reports / model artifacts --------------------------------
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
        scored_match_ids = set(self.events_by_match.keys())
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
                    "scored_event_count": len(events),
                    "avg_point_probability_player_a": sum(probabilities) / len(probabilities) if probabilities else 0.0,
                    "max_risk_score": max(risk_scores) if risk_scores else 0.0,
                    "high_risk_event_count": high_count,
                    "first_event_ts": events[0].get("event_ts"),
                    "last_event_ts": events[-1].get("event_ts"),
                    "primary_match_label": self._match_label(events[0]),
                    "replay_id": match_id,
                    "coverage_note": "Scored demo data",
                }
            )
        return sorted(summaries, key=lambda row: (-row["max_risk_score"], row["synthetic_match_id"]))

    def _build_replay_match_catalog(self) -> List[Dict[str, Any]]:
        """Build catalog of all matches from replay manifest."""
        catalog: List[Dict[str, Any]] = []
        scored_ids = set(self.events_by_match.keys())
        for match_id, events in self.replay_events_by_match.items():
            first = events[0]
            last = events[-1]
            catalog.append({
                "synthetic_match_id": match_id,
                "source_match_id": first.get("source_match_id"),
                "player_a": first.get("player_a"),
                "player_b": first.get("player_b"),
                "primary_match_label": self._match_label(first),
                "replay_id": match_id,
                "replay_event_count": len(events),
                "first_event_ts": first.get("event_ts"),
                "last_event_ts": last.get("event_ts"),
                "scored_available": match_id in scored_ids,
            })
        return sorted(catalog, key=lambda r: r.get("primary_match_label", ""))

    @staticmethod
    def _match_label(event_or_match: Dict[str, Any]) -> str:
        pa = event_or_match.get("player_a")
        pb = event_or_match.get("player_b")
        if pa and pb and pa != "Unknown" and pb != "Unknown":
            return f"{pa} vs {pb}"
        return event_or_match.get("synthetic_match_id", "Unknown Match")

    def data_coverage(self) -> Dict[str, Any]:
        """Return data coverage metadata."""
        scored_source = str(self.settings.scored_events_jsonl)
        is_full = "demo_full" in scored_source
        manifest_loaded = bool(self._replay_events_raw)
        if is_full:
            mode = "full_demo"
        elif manifest_loaded:
            mode = "manifest_catalog"
        else:
            mode = "sample"
        return {
            "scored_event_count": len(self.events),
            "scored_match_count": len(self.events_by_match),
            "replay_manifest_event_count": len(self._replay_events_raw),
            "replay_manifest_match_count": len(self.replay_events_by_match),
            "scored_data_source": scored_source,
            "replay_manifest_source": str(self.settings.replay_manifest_parquet),
            "coverage_mode": mode,
            "warning": (
                "Scored API may expose a subset unless full scored output is generated."
                if mode == "sample"
                else None
            ),
        }


@lru_cache(maxsize=1)
def get_store() -> ApiDataStore:
    return ApiDataStore()
