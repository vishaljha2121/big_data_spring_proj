#!/usr/bin/env python3
"""Benchmark JSONL scoring throughput for Milestone 3B."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from streaming.stream_scorer import StreamScorer, now_iso


def percentile(values: List[float], pct: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    idx = min(len(values) - 1, int(round((pct / 100.0) * (len(values) - 1))))
    return float(values[idx])


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-events", type=Path, required=True)
    parser.add_argument("--odds-latest", type=Path, default=Path("data/models/odds/latest.json"))
    parser.add_argument("--risk-latest", type=Path, default=Path("data/models/risk/latest.json"))
    parser.add_argument("--max-events", type=int, default=1000)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    load_start = time.perf_counter()
    scorer = StreamScorer(args.odds_latest, args.risk_latest)
    model_load_time = time.perf_counter() - load_start
    latencies: List[float] = []
    events = []
    feature_rows = []
    risks = []
    count = 0
    start = time.perf_counter()
    with args.input_events.open("r", encoding="utf-8") as handle:
        for line in handle:
            if count >= args.max_events:
                break
            if not line.strip():
                continue
            event = json.loads(line)
            event_start = time.perf_counter()
            scorer.validate_event(event)
            features = scorer.feature_builder.build_features(event)
            risks.append(scorer.risk.score(features))
            scorer.feature_builder.update_state(event)
            events.append(event)
            feature_rows.append(features)
            latencies.append((time.perf_counter() - event_start) * 1000.0)
            count += 1
    if feature_rows:
        import pandas as pd

        proba_start = time.perf_counter()
        scorer.odds.predict_proba(pd.DataFrame(feature_rows, columns=scorer.odds.feature_columns))
        proba_latency = ((time.perf_counter() - proba_start) * 1000.0) / len(feature_rows)
        latencies = [latency + proba_latency for latency in latencies]
    total = time.perf_counter() - start
    report = {
        "generated_at": now_iso(),
        "events_scored": count,
        "total_runtime_seconds": float(total),
        "events_per_second": float(count / total) if total else 0.0,
        "average_latency_ms": float(statistics.mean(latencies)) if latencies else 0.0,
        "p50_latency_ms": percentile(latencies, 50),
        "p95_latency_ms": percentile(latencies, 95),
        "p99_latency_ms": percentile(latencies, 99),
        "model_load_time_seconds": float(model_load_time),
        "output_path": "benchmark_no_event_output",
        "status": "PASSED" if count == args.max_events else "FAILED",
    }
    write_json(args.report, report)
    if report["status"] != "PASSED":
        raise SystemExit(json.dumps(report, indent=2))
    print(f"Benchmark PASSED: events={count} eps={report['events_per_second']:.2f}")


if __name__ == "__main__":
    main()
