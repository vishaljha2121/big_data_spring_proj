#!/usr/bin/env python3
"""Validate Milestone 2.5 parallelization readiness."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import jsonschema


REQUIRED_CONTRACTS = [
    "point_event_schema.json",
    "replay_manifest_schema.json",
    "odds_model_metadata_schema.json",
    "odds_model_feature_schema.json",
    "risk_model_metadata_schema.json",
    "risk_config_schema.json",
    "model_registry_schema.json",
    "model_eval_report_schema.json",
    "replay_producer_config_schema.json",
    "kafka_topic_config_schema.json",
    "parallel_workstream_handoff_schema.json",
]

REQUIRED_DOCS = [
    "docs/parallel_workstream_handoff.md",
    "docs/codex_prompt_milestone_2b.md",
    "docs/codex_prompt_milestone_3a.md",
    "README.md",
    "CODEX.md",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def file_exists(path: Path, errors: List[str], label: str) -> bool:
    if not path.exists():
        errors.append(f"missing {label}: {path}")
        return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contracts", type=Path, default=Path("contracts"))
    parser.add_argument("--out", type=Path, default=Path("data/results/parallel_readiness_report.json"))
    args = parser.parse_args()

    errors: List[str] = []
    warnings: List[str] = []

    milestone_1b_files = [
        Path("data/curated/singles_points"),
        Path("data/curated/singles_matches"),
        Path("data/curated/validation_report.json"),
        Path("docs/data_layer_audit.md"),
    ]
    milestone_2a_files = [
        Path("data/features/point_features"),
        Path("data/features/match_features"),
        Path("data/baselines/player_baselines"),
        Path("data/replay/manifests/replay_manifest_v1.parquet"),
        Path("data/features/validation_report.json"),
        Path("docs/feature_engineering_audit.md"),
        Path("docs/replay_manifest_audit.md"),
    ]
    milestone_1b_detected = all(path.exists() for path in milestone_1b_files)
    milestone_2a_detected = all(path.exists() for path in milestone_2a_files)
    if not milestone_1b_detected:
        errors.append("Milestone 1B outputs are incomplete")
    if not milestone_2a_detected:
        errors.append("Milestone 2A outputs are incomplete")

    for path in [
        Path("data/features/feature_quality_report.json"),
        Path("data/features/validation_report.json"),
        Path("data/baselines/baseline_quality_report.json"),
        Path("data/replay/replay_manifest_report.json"),
    ]:
        file_exists(path, errors, "required report")

    required_contracts_present = True
    for name in REQUIRED_CONTRACTS:
        path = args.contracts / name
        if not file_exists(path, errors, "contract"):
            required_contracts_present = False
            continue
        try:
            read_json(path)
        except Exception as exc:
            required_contracts_present = False
            errors.append(f"contract is not valid JSON: {path}: {exc}")

    topic_config = Path("infra/kafka/topic_config.json")
    if file_exists(topic_config, errors, "Kafka topic config"):
        try:
            jsonschema.validate(read_json(topic_config), read_json(args.contracts / "kafka_topic_config_schema.json"))
        except Exception as exc:
            errors.append(f"topic_config.json does not satisfy schema: {exc}")

    required_docs_present = True
    for name in REQUIRED_DOCS:
        if not file_exists(Path(name), errors, "doc"):
            required_docs_present = False

    deprecated_plan = Path("2_week_execution_plan.md")
    if deprecated_plan.exists():
        text = deprecated_plan.read_text(encoding="utf-8")
        if "DEPRECATED PLAN NOTICE" not in text:
            errors.append("2_week_execution_plan.md exists but is not marked deprecated")

    for latest in [Path("data/models/odds/latest.json"), Path("data/models/risk/latest.json")]:
        if latest.exists():
            payload = read_json(latest)
            artifact_path = Path(payload.get("artifact_path", ""))
            if payload.get("status") == "published" and not artifact_path.exists():
                errors.append(f"{latest} claims published model without artifact: {artifact_path}")
            elif payload.get("status") == "published" and not Path("data/results/model_eval/model_artifact_validation_report.json").exists():
                warnings.append(f"{latest} already exists; Milestone 2.5 expected Track A to own model publication")

    docs_text = "\n".join(path.read_text(encoding="utf-8") for path in [Path("README.md"), Path("CODEX.md"), Path("docs/parallel_workstream_handoff.md")] if path.exists())
    replay_validated = Path("data/results/replay_dry_run/validation_report.json").exists()
    if ("Milestone 3A: PASSED" in docs_text or "Kafka replay producer complete" in docs_text) and not replay_validated:
        errors.append("documentation claims Kafka replay producer is complete before Milestone 3A")

    for path in [Path("data/models"), Path("data/results"), Path("producer"), Path("infra/kafka"), Path("infra/docker")]:
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            errors.append(f"directory is not creatable: {path}: {exc}")

    track_a_ready = required_contracts_present and required_docs_present and Path("scripts/train_odds_model.py").exists() and Path("scripts/publish_model.py").exists()
    track_b_ready = required_contracts_present and required_docs_present and Path("producer/replay_producer.py").exists() and topic_config.exists()
    if not track_a_ready:
        errors.append("Track A scaffold is not ready")
    if not track_b_ready:
        errors.append("Track B scaffold is not ready")

    report = {
        "generated_at": now_iso(),
        "status": "PASSED" if not errors else "FAILED",
        "milestone_1b_detected": milestone_1b_detected,
        "milestone_2a_detected": milestone_2a_detected,
        "required_contracts_present": required_contracts_present,
        "required_docs_present": required_docs_present,
        "track_a_ready": track_a_ready,
        "track_b_ready": track_b_ready,
        "blocking_errors": errors,
        "warnings": warnings,
        "next_steps": [
            "After Milestone 2.7, create feature/milestone-3b-streaming-scorer",
            "Milestone 3B consumes tennis-point-events and writes scored local JSONL/Parquet output",
            "Keep API/frontend work blocked until streaming scorer validation passes",
        ],
    }
    write_json(args.out, report)
    if errors:
        raise SystemExit(json.dumps(report, indent=2, sort_keys=True))
    if Path("data/models/odds/latest.json").exists() and Path("data/results/replay_dry_run/validation_report.json").exists():
        print("Milestone 2.7 PASSED: model artifacts and replay dry-run are ready for Milestone 3B")
    else:
        print("Milestone 2.5 PASSED: repo is ready for Track A / Track B parallel implementation")


if __name__ == "__main__":
    main()
