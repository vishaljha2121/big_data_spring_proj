"""Match summary/detail endpoints."""

from fastapi import APIRouter, HTTPException, Query

from api.app.data_loader import get_store
from api.app.repositories import MatchRepository


router = APIRouter(prefix="/api/matches", tags=["matches"])


@router.get("")
def list_matches(limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)):
    return MatchRepository(get_store()).list_matches(limit, offset)


@router.get("/{synthetic_match_id}")
def get_match_detail(synthetic_match_id: str):
    detail = MatchRepository(get_store()).get_match(synthetic_match_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="match not found")
    return detail


@router.get("/{synthetic_match_id}/events")
def get_match_events(
    synthetic_match_id: str,
    limit: int = Query(200, ge=1, le=5000),
    offset: int = Query(0, ge=0),
):
    events = MatchRepository(get_store()).list_match_events(synthetic_match_id, limit, offset)
    if events is None:
        raise HTTPException(status_code=404, detail="match not found")
    return events
