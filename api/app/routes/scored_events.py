"""Scored event endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from api.app.data_loader import get_store
from api.app.repositories import ScoredEventRepository


router = APIRouter(prefix="/api/scored-events", tags=["scored-events"])


@router.get("")
def list_scored_events(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    risk_bucket: Optional[str] = Query(None, pattern="^(low|medium|high)$"),
    match_id: Optional[str] = None,
):
    return ScoredEventRepository(get_store()).list_events(limit, offset, risk_bucket, match_id)


@router.get("/{event_id}")
def get_scored_event(event_id: str):
    event = ScoredEventRepository(get_store()).get_event(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="scored event not found")
    return event
