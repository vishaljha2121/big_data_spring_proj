"""Replay manifest catalog endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from api.app.data_loader import get_store
from api.app.repositories import ReplayRepository


router = APIRouter(prefix="/api/replay", tags=["replay"])


@router.get("/matches")
def list_replay_matches(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
):
    return ReplayRepository(get_store()).list_matches(limit, offset, search)


@router.get("/matches/{synthetic_match_id}/events")
def get_replay_match_events(
    synthetic_match_id: str,
    limit: int = Query(1000, ge=1, le=5000),
    offset: int = Query(0, ge=0),
):
    result = ReplayRepository(get_store()).get_match_events(synthetic_match_id, limit, offset)
    if result is None:
        raise HTTPException(status_code=404, detail="replay match not found")
    return result
