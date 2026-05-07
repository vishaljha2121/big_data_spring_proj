#!/usr/bin/env python3
"""Publish successfully trained outcome models from staging to production."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def publish_target(target_name: str) -> bool:
    models_dir = ROOT / f"data/models/outcomes/{target_name}"
    staging_dir = models_dir / "staging"
    report_path = staging_dir / "eval_report.json"
    
    if not staging_dir.exists() or not report_path.exists():
        print(f"[{target_name.upper()}] No staging model found.")
        return False
        
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report.get("status") != "PASSED":
        print(f"[{target_name.upper()}] Model failed quality gates. Not publishing.")
        return False
        
    publish_dir = models_dir / "v1"
    if publish_dir.exists():
        shutil.rmtree(publish_dir)
    shutil.copytree(staging_dir, publish_dir)
    
    # Create latest.json pointer
    metadata = json.loads((publish_dir / "metadata.json").read_text(encoding="utf-8"))
    latest = {
        "schema_version": "outcome_model_registry_v1",
        "model_type": f"outcome_{target_name}",
        "latest_version": "v1",
        "published_at": metadata["trained_at"],
        "path": f"data/models/outcomes/{target_name}/v1",
        "feature_schema_hash": metadata.get("feature_schema_hash", ""),
        "validation_auc": metadata["validation_auc"],
        "test_auc": metadata["test_auc"],
        "training_script": metadata["training_script"],
    }
    write_json(models_dir / "latest.json", latest)
    print(f"[{target_name.upper()}] Successfully published v1.")
    return True

def main() -> None:
    targets = ["game", "set", "match"]
    results = {}
    
    for t in targets:
        results[t] = publish_target(t)
        
    report = {
        "published_targets": [t for t, v in results.items() if v],
        "blocked_targets": [t for t, v in results.items() if not v]
    }
    out_dir = ROOT / "data/results/outcome_models"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "outcome_model_publication_report.json", report)

if __name__ == "__main__":
    main()
