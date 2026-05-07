#!/usr/bin/env python3
"""Run Spark Structured Streaming scorer from Kafka to local scored sinks."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import socket
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from spark_streaming.kafka_streaming_scorer import StreamingRunState, make_foreach_batch, write_run_report
from streaming.stream_scorer import StreamScorer


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_not_executed(path: Path, blocker: str) -> None:
    payload = {
        "generated_at": now_iso(),
        "status": "NOT_EXECUTED",
        "blocking_errors": [blocker],
        "warnings": [],
    }
    write_run_report(path, payload)
    print(json.dumps(payload, indent=2))


def kafka_reachable(bootstrap_servers: str, timeout: float = 2.0) -> bool:
    host, _, port_text = bootstrap_servers.partition(":")
    try:
        with socket.create_connection((host or "localhost", int(port_text or "9092")), timeout=timeout):
            return True
    except OSError:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstrap-servers", default="localhost:9092")
    parser.add_argument("--topic", default="tennis-point-events")
    parser.add_argument("--odds-latest", type=Path, default=Path("data/models/odds/latest.json"))
    parser.add_argument("--risk-latest", type=Path, default=Path("data/models/risk/latest.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/results/spark_streaming"))
    parser.add_argument("--checkpoint-dir", type=Path, default=Path("data/checkpoints/spark_streaming_scorer"))
    parser.add_argument("--max-events", type=int, default=1000)
    parser.add_argument("--timeout-seconds", type=int, default=60)
    args = parser.parse_args()

    report_path = args.output_dir / "spark_streaming_run_report.json"
    if not kafka_reachable(args.bootstrap_servers):
        write_not_executed(report_path, f"Kafka broker is not reachable at {args.bootstrap_servers}")
        raise SystemExit(2)
    if not shutil.which("java"):
        write_not_executed(report_path, "Java runtime is not available for Spark")
        raise SystemExit(2)

    try:
        from spark_streaming.spark_session import create_spark_session
    except Exception as exc:
        write_not_executed(report_path, f"Spark session helper import failed: {exc}")
        raise SystemExit(2)

    try:
        spark = create_spark_session()
    except Exception as exc:
        write_not_executed(report_path, f"Spark session could not start: {exc}")
        raise SystemExit(2)

    output_jsonl_dir = args.output_dir / "scored_events_jsonl"
    output_parquet_dir = args.output_dir / "scored_events_parquet"
    output_jsonl_dir.mkdir(parents=True, exist_ok=True)
    output_parquet_dir.mkdir(parents=True, exist_ok=True)
    args.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    output_jsonl = output_jsonl_dir / "part-00000.jsonl"
    if output_jsonl.exists():
        output_jsonl.unlink()

    scorer = StreamScorer(args.odds_latest, args.risk_latest)
    state = StreamingRunState(max_events=args.max_events)
    started_at = now_iso()
    start = time.perf_counter()
    errors = []

    try:
        kafka_df = (
            spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", args.bootstrap_servers)
            .option("subscribe", args.topic)
            .option("startingOffsets", "earliest")
            .load()
        )
        query = (
            kafka_df.writeStream.foreachBatch(
                make_foreach_batch(scorer, output_jsonl, output_parquet_dir, state)
            )
            .option("checkpointLocation", str(args.checkpoint_dir))
            .trigger(processingTime="2 seconds")
            .start()
        )
        deadline = time.time() + args.timeout_seconds
        while time.time() < deadline and state.scored_count < args.max_events:
            query.processAllAvailable()
            time.sleep(0.5)
        query.stop()
    except Exception as exc:
        errors.append(str(exc))
    finally:
        spark.stop()

    elapsed = time.perf_counter() - start
    status = "PASSED" if not errors and state.scored_count >= args.max_events else "FAILED"
    report = {
        "generated_at": now_iso(),
        "started_at": started_at,
        "status": status,
        "bootstrap_servers": args.bootstrap_servers,
        "topic": args.topic,
        "max_events": args.max_events,
        "input_count": state.input_count,
        "scored_count": state.scored_count,
        "invalid_count": state.invalid_count,
        "elapsed_seconds": elapsed,
        "checkpoint_dir": str(args.checkpoint_dir),
        "output_jsonl": str(output_jsonl),
        "output_parquet_dir": str(output_parquet_dir),
        "batch_reports": state.batch_reports,
        "warnings": [],
        "blocking_errors": errors,
    }
    write_run_report(report_path, report)
    print(json.dumps(report, indent=2))
    if status != "PASSED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
