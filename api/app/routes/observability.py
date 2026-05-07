"""Observability endpoints for the Tennis Analytics API."""

from fastapi import APIRouter
from api.app.data_loader import get_store
from observability.logging_utils import now_iso

router = APIRouter(prefix="/api/observability", tags=["observability"])

def load_observability_data():
    store = get_store()
    from observability.metrics import extract_api_metrics, extract_scoring_metrics, extract_streaming_metrics
    from observability.drift import compute_score_shift
    from observability.quality_alerts import check_data_quality
    
    # Normally we load from observability_snapshot, but we compute live from store if needed
    val_probs = [] # Omitted for live endpoint efficiency, relies on precomputed snapshot if available
    
    # We will just load the snapshot if it exists
    import json
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    snap_path = root / "data/results/observability/observability_snapshot.json"
    if snap_path.exists():
        return json.loads(snap_path.read_text())
    
    return {
        "generated_at": now_iso(),
        "trace_id": "unavailable",
        "api_metrics": extract_api_metrics(store),
        "scoring_metrics": extract_scoring_metrics(store),
        "streaming_metrics": extract_streaming_metrics(store),
        "drift_summary": {"status": "unavailable"},
        "active_alerts": check_data_quality(store)
    }

@router.get("/summary")
def get_observability_summary():
    data = load_observability_data()
    return {
        "generated_at": data["generated_at"],
        "api_status": data["api_metrics"].get("status", "unknown"),
        "scoring_status": "OK" if data["scoring_metrics"].get("events_scored", 0) > 0 else "WARNING",
        "streaming_status": data["streaming_metrics"].get("status", "unknown"),
        "drift_summary": data["drift_summary"],
        "active_alerts": data["active_alerts"]
    }

@router.get("/alerts")
def get_observability_alerts():
    data = load_observability_data()
    return {
        "generated_at": data["generated_at"],
        "data_quality_alerts": data["active_alerts"],
        "runtime_warnings": []
    }

@router.get("/metrics")
def get_observability_metrics():
    data = load_observability_data()
    return {
        "api": data["api_metrics"],
        "scoring": data["scoring_metrics"],
        "streaming": data["streaming_metrics"],
        "model": data["drift_summary"]
    }
