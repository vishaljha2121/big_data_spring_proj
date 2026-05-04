"""Risk summary endpoints."""

from typing import Optional

from fastapi import APIRouter, Query

from api.app.data_loader import get_store
from api.app.repositories import RiskRepository


router = APIRouter(prefix="/api/risk", tags=["risk"])


@router.get("/summary")
def risk_summary():
    return RiskRepository(get_store()).summary()


@router.get("/events")
def risk_events(
    bucket: Optional[str] = Query(None, pattern="^(low|medium|high)$"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    return RiskRepository(get_store()).events(bucket, limit, offset)
