"""Health and readiness endpoints."""

from fastapi import APIRouter

from api.app.config import settings
from api.app.data_loader import get_store
from api.app.schemas import now_iso


router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "service": settings.service_name, "timestamp": now_iso(), "version": settings.version}


@router.get("/ready")
def ready():
    store = get_store()
    checks = store.readiness_checks()
    status = "ready" if all(checks.values()) else "not_ready"
    return {"status": status, "checks": checks, "timestamp": now_iso()}
