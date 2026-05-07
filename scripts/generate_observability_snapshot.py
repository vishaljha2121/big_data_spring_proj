#!/usr/bin/env python3
"""Generate local observability snapshot."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.app.data_loader import get_store
from observability.logging_utils import now_iso, generate_trace_id
from observability.drift import compute_score_shift
from observability.quality_alerts import check_data_quality
from observability.metrics import extract_api_metrics, extract_scoring_metrics, extract_streaming_metrics

def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def main():
    store = get_store()
    
    trace_id = generate_trace_id()
    
    api_metrics = extract_api_metrics(store)
    scoring_metrics = extract_scoring_metrics(store)
    streaming_metrics = extract_streaming_metrics(store)
    alerts = check_data_quality(store)
    
    # Drift
    val_probs = []
    if store.odds_eval_report and "validation_predictions" in str(store.odds_latest.get("metadata_path", "")):
        pass # To fully do this we need to load validation predictions.
        
    val_path = ROOT / "data/models/odds/staging/validation_predictions.json"
    if val_path.exists():
        val_probs = json.loads(val_path.read_text())["predictions"]
        
    scored_probs = [float(e.get("point_probability_player_a", 0.5)) for e in store.events]
    drift_report = compute_score_shift(val_probs, scored_probs)
    
    snapshot = {
        "generated_at": now_iso(),
        "trace_id": trace_id,
        "api_metrics": api_metrics,
        "scoring_metrics": scoring_metrics,
        "streaming_metrics": streaming_metrics,
        "drift_summary": drift_report,
        "active_alerts": alerts
    }
    
    out_dir = ROOT / "data/results/observability"
    write_json(out_dir / "observability_snapshot.json", snapshot)
    write_json(out_dir / "api_metrics_summary.json", api_metrics)
    write_json(out_dir / "scoring_metrics_summary.json", scoring_metrics)
    write_json(out_dir / "streaming_metrics_summary.json", streaming_metrics)
    write_json(out_dir / "model_score_drift_report.json", drift_report)
    write_json(out_dir / "data_quality_alerts.json", {"alerts": alerts})
    
    print(f"Generated observability snapshot with trace_id {trace_id}")

if __name__ == "__main__":
    main()
