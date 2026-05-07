#!/usr/bin/env python3
"""Publish and consume a bounded Kafka replay sample, then write a runtime report."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run(command: List[str], timeout: int = 120) -> Dict[str, Any]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
    return {
        "command": " ".join(command),
        "returncode": result.returncode,
        "stdout": result.stdout[-5000:],
        "stderr": result.stderr[-5000:],
    }


def write_report(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstrap-servers", default="localhost:9092")
    parser.add_argument("--topic", default="tennis-point-events")
    parser.add_argument("--manifest", type=Path, default=Path("data/replay/manifests/replay_manifest_v1.parquet"))
    parser.add_argument("--config", type=Path, default=Path("infra/kafka/topic_config.json"))
    parser.add_argument("--max-events", type=int, default=1000)
    parser.add_argument("--report", type=Path, default=Path("data/results/kafka_runtime/kafka_replay_smoke_report.json"))
    args = parser.parse_args()

    producer_cmd = [
        ".venv/bin/python",
        "producer/replay_producer.py",
        "--manifest",
        str(args.manifest),
        "--config",
        str(args.config),
        "--bootstrap-servers",
        args.bootstrap_servers,
        "--topic",
        args.topic,
        "--max-events",
        str(args.max_events),
        "--speed",
        "0",
    ]
    consume_report = Path("data/results/kafka_runtime/kafka_consume_sample_report.json")
    consumer_cmd = [
        ".venv/bin/python",
        "scripts/consume_replay_sample.py",
        "--bootstrap-servers",
        args.bootstrap_servers,
        "--topic",
        args.topic,
        "--max-events",
        str(args.max_events),
        "--group-id",
        f"spark-tennis-validation-{int(datetime.now().timestamp())}",
        "--report",
        str(consume_report),
    ]

    producer = run(producer_cmd, timeout=180)
    consumer = run(consumer_cmd, timeout=180) if producer["returncode"] == 0 else None
    consumed_report = None
    if consume_report.exists():
        consumed_report = json.loads(consume_report.read_text(encoding="utf-8"))
    errors = []
    if producer["returncode"] != 0:
        errors.append("replay producer failed")
    if not consumer or consumer["returncode"] != 0:
        errors.append("Kafka sample consumer failed")
    if consumed_report and consumed_report.get("events_checked", 0) < args.max_events:
        errors.append("consumer validated fewer than expected events")

    report = {
        "generated_at": now_iso(),
        "status": "PASSED" if not errors else "FAILED",
        "bootstrap_servers": args.bootstrap_servers,
        "topic": args.topic,
        "expected_events": args.max_events,
        "producer": producer,
        "consumer": consumer,
        "consume_report": consumed_report,
        "warnings": [],
        "blocking_errors": errors,
    }
    write_report(args.report, report)
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
