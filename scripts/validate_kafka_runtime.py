#!/usr/bin/env python3
"""Validate local Kafka runtime and canonical topic configuration."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "data/results/kafka_runtime/kafka_runtime_report.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run(command: List[str], timeout: int = 20) -> Dict[str, Any]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
    return {
        "command": " ".join(command),
        "returncode": result.returncode,
        "stdout": result.stdout[-4000:],
        "stderr": result.stderr[-4000:],
    }


def write_report(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_partitions(describe_output: str) -> int | None:
    tokens = describe_output.replace("\t", " ").split()
    for index, token in enumerate(tokens):
        if token.startswith("PartitionCount:"):
            value = token.split(":", 1)[1]
            if not value and index + 1 < len(tokens):
                value = tokens[index + 1]
            try:
                return int(value)
            except ValueError:
                return None
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "infra/kafka/topic_config.json")
    parser.add_argument("--container", default="tennis-kafka")
    parser.add_argument("--kafka-topics-bin", default="/opt/kafka/bin/kafka-topics.sh")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    errors: List[str] = []
    warnings: List[str] = []
    checks: Dict[str, Any] = {}

    docker_path = shutil.which("docker")
    checks["docker_available"] = bool(docker_path)
    checks["docker_path"] = docker_path
    if not docker_path:
        errors.append("docker command not available")
        report = {
            "generated_at": now_iso(),
            "status": "NOT_EXECUTED",
            "topic": cfg["topic"],
            "partition_count_expected": cfg["partitions"],
            "checks": checks,
            "warnings": warnings,
            "blocking_errors": errors,
        }
        write_report(args.report, report)
        print(json.dumps(report, indent=2))
        raise SystemExit(2)

    docker_info = run(["docker", "info"], timeout=20)
    checks["docker_info"] = docker_info
    if docker_info["returncode"] != 0:
        errors.append("docker daemon is not available")
        report = {
            "generated_at": now_iso(),
            "status": "NOT_EXECUTED",
            "topic": cfg["topic"],
            "partition_count_expected": cfg["partitions"],
            "partition_count_actual": None,
            "checks": checks,
            "warnings": warnings,
            "blocking_errors": errors,
        }
        write_report(args.report, report)
        print(json.dumps(report, indent=2))
        raise SystemExit(2)

    ps = run(["docker", "ps", "--filter", f"name={args.container}", "--format", "{{.Names}}"], timeout=20)
    checks["container_ps"] = ps
    container_running = args.container in ps["stdout"].splitlines()
    checks["container_running"] = container_running
    if not container_running:
        errors.append(f"Kafka container {args.container} is not running")

    describe = None
    partitions = None
    if container_running:
        describe = run(
            [
                "docker",
                "exec",
                args.container,
                args.kafka_topics_bin,
                "--bootstrap-server",
                "localhost:9092",
                "--describe",
                "--topic",
                cfg["topic"],
            ],
            timeout=30,
        )
        checks["topic_describe"] = describe
        if describe["returncode"] != 0:
            errors.append(f"topic {cfg['topic']} does not exist or cannot be described")
        partitions = parse_partitions(describe["stdout"] if describe else "")
        checks["partition_count_actual"] = partitions
        if partitions != cfg["partitions"]:
            errors.append(f"expected {cfg['partitions']} partitions, found {partitions}")

    report = {
        "generated_at": now_iso(),
        "status": "PASSED" if not errors else "FAILED",
        "topic": cfg["topic"],
        "partition_count_expected": cfg["partitions"],
        "partition_count_actual": partitions,
        "checks": checks,
        "warnings": warnings,
        "blocking_errors": errors,
    }
    write_report(args.report, report)
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
