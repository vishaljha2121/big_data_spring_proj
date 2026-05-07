"""API configuration paths."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    service_name: str = "tennis-scoring-api"
    version: str = "api_v1"
    scored_events_jsonl: Path = field(default_factory=lambda: Path(
        os.environ.get(
            "TENNIS_SCORED_EVENTS_PATH",
            str(ROOT / "data/results/streaming_scoring/scored_events_sample.jsonl"),
        )
    ))
    scored_events_parquet: Path = ROOT / "data/results/streaming_scoring/scored_events_sample.parquet"
    scoring_run_report: Path = ROOT / "data/results/streaming_scoring/scoring_run_report.json"
    scoring_validation_report: Path = ROOT / "data/results/streaming_scoring/scoring_validation_report.json"
    scoring_benchmark_report: Path = ROOT / "data/results/streaming_scoring/scoring_benchmark_report.json"
    odds_latest: Path = ROOT / "data/models/odds/latest.json"
    risk_latest: Path = ROOT / "data/models/risk/latest.json"
    odds_eval_report: Path = ROOT / "data/results/model_eval/odds_model_eval_report.json"
    risk_eval_report: Path = ROOT / "data/results/model_eval/risk_model_eval_report.json"
    replay_manifest_parquet: Path = field(default_factory=lambda: Path(
        os.environ.get(
            "TENNIS_REPLAY_MANIFEST_PATH",
            str(ROOT / "data/replay/manifests/replay_manifest_v1.parquet"),
        )
    ))
    replay_manifest_report: Path = ROOT / "data/replay/manifests/replay_manifest_v1.json"
    full_scored_events_jsonl: Path = ROOT / "data/results/streaming_scoring/scored_events_demo_full.jsonl"


settings = Settings()
