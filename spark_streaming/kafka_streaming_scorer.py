"""Spark Structured Streaming Kafka scorer using foreachBatch."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from spark_streaming.sinks import append_jsonl, write_parquet_batch
from streaming.stream_scorer import StreamScorer


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass
class StreamingRunState:
    max_events: int
    scored_count: int = 0
    input_count: int = 0
    invalid_count: int = 0
    batch_reports: List[Dict[str, Any]] = field(default_factory=list)
    stopped_for_max_events: bool = False


def parse_event_value(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, bytes):
        value = value.decode("utf-8")
    return json.loads(value)


def score_event_batch(
    events: List[Dict[str, Any]],
    scorer: StreamScorer,
    output_jsonl: Path,
    output_parquet_dir: Path,
    batch_id: int = 0,
    max_remaining: int | None = None,
) -> Dict[str, Any]:
    start = time.perf_counter()
    scored: List[Dict[str, Any]] = []
    invalid: List[Dict[str, Any]] = []
    limit = len(events) if max_remaining is None else max(0, min(len(events), max_remaining))
    for event in events[:limit]:
        try:
            scored.append(scorer.score_event(event))
        except Exception as exc:
            invalid.append({"synthetic_event_id": event.get("synthetic_event_id"), "error": str(exc)})
    append_jsonl(output_jsonl, scored)
    parquet_path = write_parquet_batch(output_parquet_dir, scored, batch_id)
    latency = time.perf_counter() - start
    return {
        "batch_id": int(batch_id),
        "input_count": len(events),
        "attempted_count": limit,
        "scored_count": len(scored),
        "invalid_count": len(invalid),
        "invalid_examples": invalid[:5],
        "jsonl_path": str(output_jsonl),
        "parquet_batch_path": str(parquet_path) if parquet_path else None,
        "latency_seconds": latency,
    }


def make_foreach_batch(
    scorer: StreamScorer,
    output_jsonl: Path,
    output_parquet_dir: Path,
    state: StreamingRunState,
):
    def foreach_batch(batch_df, batch_id: int) -> None:
        if state.stopped_for_max_events:
            return
        pdf = batch_df.selectExpr("CAST(value AS STRING) AS value").toPandas()
        events = []
        invalid_parse = 0
        for raw_value in pdf["value"].tolist():
            try:
                events.append(parse_event_value(raw_value))
            except Exception:
                invalid_parse += 1
        remaining = state.max_events - state.scored_count
        report = score_event_batch(events, scorer, output_jsonl, output_parquet_dir, batch_id, remaining)
        report["parse_invalid_count"] = invalid_parse
        state.batch_reports.append(report)
        state.input_count += len(events) + invalid_parse
        state.scored_count += report["scored_count"]
        state.invalid_count += report["invalid_count"] + invalid_parse
        if state.scored_count >= state.max_events:
            state.stopped_for_max_events = True

    return foreach_batch


def write_run_report(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

