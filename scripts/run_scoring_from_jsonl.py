#!/usr/bin/env python3
"""Score replay point events from JSONL using published odds/risk artifacts."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from streaming.stream_scorer import StreamScorer, now_iso


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def percentile(values: List[float], pct: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    idx = min(len(values) - 1, int(round((pct / 100.0) * (len(values) - 1))))
    return float(values[idx])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-events", type=Path, required=True)
    parser.add_argument("--odds-latest", type=Path, default=Path("data/models/odds/latest.json"))
    parser.add_argument("--risk-latest", type=Path, default=Path("data/models/risk/latest.json"))
    parser.add_argument("--output-jsonl", type=Path, required=True)
    parser.add_argument("--output-parquet", type=Path, default=None)
    parser.add_argument("--max-events", type=int, default=None)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    scorer = StreamScorer(args.odds_latest, args.risk_latest)
    scored: List[Dict[str, Any]] = []
    events: List[Dict[str, Any]] = []
    feature_rows: List[Dict[str, Any]] = []
    risks: List[Dict[str, Any]] = []
    latencies: List[float] = []
    errors: List[str] = []
    input_count = 0
    with args.input_events.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            if args.max_events is not None and input_count >= args.max_events:
                break
            if not line.strip():
                continue
            input_count += 1
            try:
                event = json.loads(line)
                start = time.perf_counter()
                scorer.validate_event(event)
                features = scorer.feature_builder.build_features(event)
                risk = scorer.risk.score(features)
                scorer.feature_builder.update_state(event)
                events.append(event)
                feature_rows.append(features)
                risks.append(risk)
                latencies.append((time.perf_counter() - start) * 1000.0)
            except Exception as exc:
                errors.append(f"line {line_no}: {exc}")

    if feature_rows:
        proba_start = time.perf_counter()
        probabilities = scorer.odds.predict_proba(pd.DataFrame(feature_rows, columns=scorer.odds.feature_columns))
        proba_latency = ((time.perf_counter() - proba_start) * 1000.0) / len(feature_rows)
        scored = [
            scorer.format_scored_event(event, probability, risk, latency + proba_latency)
            for event, probability, risk, latency in zip(events, probabilities, risks, latencies)
        ]

    args.output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with args.output_jsonl.open("w", encoding="utf-8") as handle:
        for event in scored:
            handle.write(json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n")

    parquet_path = None
    warnings: List[str] = []
    if args.output_parquet is not None:
        try:
            pd.DataFrame(scored).to_parquet(args.output_parquet, index=False)
            parquet_path = str(args.output_parquet)
        except Exception as exc:
            warnings.append(f"Parquet output skipped: {exc}")

    latencies = [event["scoring_latency_ms"] for event in scored]
    report = {
        "generated_at": now_iso(),
        "input_event_count": input_count,
        "scored_event_count": len(scored),
        "invalid_event_count": len(errors),
        "feature_schema_hash": scorer.odds.feature_schema_hash,
        "odds_model_version": scorer.odds.version,
        "risk_model_version": scorer.risk_loader.version,
        "defaulted_features": scorer.defaulted_features,
        "missing_features": scorer.missing_features,
        "average_scoring_latency_ms": float(statistics.mean(latencies)) if latencies else 0.0,
        "p95_scoring_latency_ms": percentile(latencies, 95),
        "output_jsonl": str(args.output_jsonl),
        "output_parquet": parquet_path,
        "status": "PASSED" if scored and not errors else "FAILED",
        "warnings": warnings,
        "blocking_errors": errors[:10],
    }
    write_json(args.report, report)
    if report["status"] != "PASSED":
        raise SystemExit(json.dumps(report, indent=2))
    print(f"Scored {len(scored)} events to {args.output_jsonl}")


if __name__ == "__main__":
    main()
