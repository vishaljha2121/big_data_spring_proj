#!/usr/bin/env python3
"""Validate the local FastAPI contract without starting a server."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api.app.main import app
from api.app.schemas import now_iso


ROOT = Path(__file__).resolve().parents[1]


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    client = TestClient(app)
    endpoints = {
        "health": "/health",
        "ready": "/ready",
        "summary": "/api/summary",
        "scored_events": "/api/scored-events?limit=5",
        "matches": "/api/matches?limit=5",
        "risk_summary": "/api/risk/summary",
        "models_current": "/api/models/current",
        "benchmarks_latest": "/api/benchmarks/latest",
        "data_coverage": "/api/data/coverage",
        "replay_matches": "/api/replay/matches?limit=5",
        "observability_summary": "/api/observability/summary",
        "observability_alerts": "/api/observability/alerts",
        "observability_metrics": "/api/observability/metrics",
        "models_outcomes": "/api/models/outcomes",
    }
    samples: Dict[str, Any] = {}
    errors = []
    for name, path in endpoints.items():
        response = client.get(path)
        if response.status_code != 200:
            errors.append(f"{path} returned {response.status_code}")
            continue
        samples[name] = response.json()
    if samples.get("ready", {}).get("status") != "ready":
        errors.append("/ready is not ready")
    match_items = samples.get("matches", {}).get("items", [])
    if match_items:
        match_id = match_items[0]["synthetic_match_id"]
        response = client.get(f"/api/matches/{match_id}")
        if response.status_code != 200:
            errors.append(f"/api/matches/{match_id} returned {response.status_code}")
        else:
            samples["match_detail"] = response.json()
        response = client.get(f"/api/matches/{match_id}/events?limit=5")
        if response.status_code != 200:
            errors.append(f"/api/matches/{match_id}/events returned {response.status_code}")
        else:
            samples["match_events"] = response.json()
    event_items = samples.get("scored_events", {}).get("items", [])
    if event_items:
        event_id = event_items[0]["event_id"]
        response = client.get(f"/api/scored-events/{event_id}")
        if response.status_code != 200:
            errors.append(f"/api/scored-events/{event_id} returned {response.status_code}")
        else:
            samples["scored_event_detail"] = response.json()

    openapi = app.openapi()
    write_json(ROOT / "contracts/api_openapi_snapshot.json", openapi)
    write_json(ROOT / "contracts/api_response_examples.json", samples)
    write_json(ROOT / "data/results/api_validation/sample_responses.json", samples)
    report = {
        "generated_at": now_iso(),
        "status": "PASSED" if not errors else "FAILED",
        "endpoints_checked": list(endpoints.values()),
        "scored_event_count": samples.get("summary", {}).get("scored_event_count"),
        "unique_match_count": samples.get("summary", {}).get("unique_match_count"),
        "blocking_errors": errors,
    }
    write_json(ROOT / "data/results/api_validation/api_validation_report.json", report)
    if errors:
        raise SystemExit(json.dumps(report, indent=2))
    print("API contract validation PASSED")


if __name__ == "__main__":
    main()
