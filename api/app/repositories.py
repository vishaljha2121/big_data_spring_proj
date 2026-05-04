"""Query helpers over the in-memory scored-event store."""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional

from api.app.data_loader import ApiDataStore
from api.app.schemas import RISK_DISCLAIMER


def paginate(items: List[Dict[str, Any]], limit: int, offset: int) -> Dict[str, Any]:
    limit = max(1, min(limit, 1000))
    offset = max(0, offset)
    page = items[offset : offset + limit]
    return {"items": page, "limit": limit, "offset": offset, "count": len(page), "total_available": len(items)}


class ScoredEventRepository:
    def __init__(self, store: ApiDataStore):
        self.store = store

    def list_events(
        self,
        limit: int = 100,
        offset: int = 0,
        risk_bucket: Optional[str] = None,
        match_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        rows = self.store.events
        if risk_bucket:
            rows = [row for row in rows if row.get("risk_bucket") == risk_bucket]
        if match_id:
            rows = [row for row in rows if row.get("synthetic_match_id") == match_id or row.get("source_match_id") == match_id]
        compact = [
            {
                "synthetic_match_id": row.get("synthetic_match_id"),
                "event_id": row.get("event_id"),
                "replay_order": row.get("replay_order"),
                "player_a": row.get("player_a"),
                "player_b": row.get("player_b"),
                "point_probability_player_a": row.get("point_probability_player_a"),
                "point_probability_player_b": row.get("point_probability_player_b"),
                "risk_score": row.get("risk_score"),
                "risk_bucket": row.get("risk_bucket"),
                "primary_risk_signal": row.get("primary_risk_signal"),
                "event_ts": row.get("event_ts"),
                "scored_at": row.get("scored_at"),
            }
            for row in rows
        ]
        return paginate(compact, limit, offset)

    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        return self.store.event_by_id.get(event_id)


class MatchRepository:
    def __init__(self, store: ApiDataStore):
        self.store = store

    def list_matches(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        return paginate(self.store.match_summaries, limit, offset)

    def get_match(self, synthetic_match_id: str) -> Optional[Dict[str, Any]]:
        events = self.store.events_by_match.get(synthetic_match_id)
        if not events:
            return None
        summary = next(row for row in self.store.match_summaries if row["synthetic_match_id"] == synthetic_match_id)
        return {
            "summary": summary,
            "events": events,
            "risk_summary": self._risk_summary(events),
            "point_probability_timeline": [
                {
                    "replay_order": row.get("replay_order"),
                    "event_ts": row.get("event_ts"),
                    "point_probability_player_a": row.get("point_probability_player_a"),
                    "point_probability_player_b": row.get("point_probability_player_b"),
                    "risk_score": row.get("risk_score"),
                }
                for row in events
            ],
        }

    def list_match_events(self, synthetic_match_id: str, limit: int = 200, offset: int = 0) -> Optional[Dict[str, Any]]:
        events = self.store.events_by_match.get(synthetic_match_id)
        if events is None:
            return None
        return paginate(events, limit, offset)

    @staticmethod
    def _risk_summary(events: List[Dict[str, Any]]) -> Dict[str, Any]:
        counts = Counter(row.get("risk_bucket", "unknown") for row in events)
        return {
            "count_by_bucket": dict(counts),
            "max_risk_score": max(float(row.get("risk_score", 0.0)) for row in events) if events else 0.0,
            "disclaimer": RISK_DISCLAIMER,
        }


class RiskRepository:
    def __init__(self, store: ApiDataStore):
        self.store = store

    def summary(self) -> Dict[str, Any]:
        bucket_counts = Counter(row.get("risk_bucket", "unknown") for row in self.store.events)
        top_events = sorted(self.store.events, key=lambda row: float(row.get("risk_score", 0.0)), reverse=True)[:10]
        top_matches = sorted(self.store.match_summaries, key=lambda row: float(row.get("max_risk_score", 0.0)), reverse=True)[:10]
        return {
            "count_by_bucket": dict(bucket_counts),
            "top_risk_events": top_events,
            "top_risk_matches": top_matches,
            "disclaimer": RISK_DISCLAIMER,
        }

    def events(self, bucket: Optional[str], limit: int, offset: int) -> Dict[str, Any]:
        rows = self.store.events
        if bucket:
            rows = [row for row in rows if row.get("risk_bucket") == bucket]
        rows = sorted(rows, key=lambda row: float(row.get("risk_score", 0.0)), reverse=True)
        return paginate(rows, limit, offset)
