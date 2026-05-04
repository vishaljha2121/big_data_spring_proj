"""Benchmark and summary endpoints."""

from fastapi import APIRouter

from api.app.data_loader import get_store
from api.app.schemas import RISK_DISCLAIMER


router = APIRouter(tags=["benchmarks"])


@router.get("/api/summary")
def system_summary():
    store = get_store()
    benchmark = store.scoring_benchmark_report
    warnings = []
    if not store.events:
        warnings.append("No scored events loaded.")
    return {
        "scored_event_count": len(store.events),
        "unique_match_count": len(store.events_by_match),
        "odds_model_version": store.odds_latest.get("version"),
        "risk_model_version": store.risk_latest.get("version"),
        "benchmark_events_per_second": benchmark.get("events_per_second"),
        "average_latency_ms": benchmark.get("average_latency_ms"),
        "p95_latency_ms": benchmark.get("p95_latency_ms"),
        "warnings": warnings,
        "risk_disclaimer": RISK_DISCLAIMER,
    }


@router.get("/api/benchmarks/latest")
def latest_benchmark():
    store = get_store()
    return {
        "scoring_benchmark_report": store.scoring_benchmark_report,
        "scoring_run_report": store.scoring_run_report,
        "scoring_validation_report": store.scoring_validation_report,
        "odds_model_eval_report": store.odds_eval_report,
        "risk_model_eval_report": store.risk_eval_report,
        "validation_status": {
            "scoring": store.scoring_validation_report.get("status"),
            "benchmark": store.scoring_benchmark_report.get("status"),
        },
    }
