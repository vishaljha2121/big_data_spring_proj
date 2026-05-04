#!/usr/bin/env python3
"""Fast final presentation preflight for the local tennis analytics demo."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/results/final_demo/final_preflight_report.json"


REQUIRED_ARTIFACTS = [
    "data/features/point_features",
    "data/baselines/player_baselines",
    "data/replay/manifests/replay_manifest_v1.parquet",
    "data/models/odds/latest.json",
    "data/models/risk/latest.json",
    "data/results/replay_dry_run/sample_events.jsonl",
    "data/results/streaming_scoring/scored_events_sample.jsonl",
    "data/results/streaming_scoring/scoring_validation_report.json",
]

REQUIRED_API = [
    "api/app/main.py",
    "contracts/api_openapi_snapshot.json",
    "contracts/api_response_examples.json",
    "data/results/api_validation/api_validation_report.json",
]

REQUIRED_FRONTEND = [
    "frontend/package.json",
    "frontend/index.html",
    "frontend/vite.config.js",
    "frontend/.env.example",
    "frontend/src/App.jsx",
    "frontend/src/main.jsx",
    "data/results/frontend_validation/frontend_validation_report.json",
]

REQUIRED_DOCS = [
    "README.md",
    "CODEX.md",
    "docs/api_contract.md",
    "docs/frontend_dashboard_audit.md",
    "docs/final_demo_runbook.md",
    "docs/final_submission_checklist.md",
    "docs/final_project_status.md",
]

PASSED_REPORTS = {
    "api_validation": "data/results/api_validation/api_validation_report.json",
    "frontend_validation": "data/results/frontend_validation/frontend_validation_report.json",
    "scoring_validation": "data/results/streaming_scoring/scoring_validation_report.json",
    "feature_validation": "data/features/validation_report.json",
    "parallel_readiness": "data/results/parallel_readiness_report.json",
}

STALE_STATUS_FILES = [
    "README.md",
    "CODEX.md",
    "docs/next_implementation_steps.md",
    "docs/final_project_status.md",
    "docs/final_demo_runbook.md",
]

STALE_PHRASES = [
    "Milestone 4B: pending",
    "Milestone 4B is pending",
    "Milestone 4B remains",
    "frontend is blocked",
    "frontend remains blocked",
    "Proceed to Milestone 2B",
    "Proceed to **Milestone 2B",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def exists_check(paths: List[str]) -> Dict[str, Dict[str, Any]]:
    result: Dict[str, Dict[str, Any]] = {}
    for rel in paths:
        path = ROOT / rel
        ok = path.exists()
        if ok and path.is_dir():
            ok = any(path.glob("*"))
        result[rel] = {"exists": ok, "type": "dir" if path.is_dir() else "file"}
    return result


def report_status_checks() -> Dict[str, Dict[str, Any]]:
    checks: Dict[str, Dict[str, Any]] = {}
    for name, rel in PASSED_REPORTS.items():
        path = ROOT / rel
        payload: Dict[str, Any] = {}
        status = "MISSING"
        if path.exists():
            try:
                payload = read_json(path)
                status = str(payload.get("status") or payload.get("milestone_status") or "").upper()
            except Exception as exc:  # pragma: no cover - defensive report detail
                status = f"INVALID_JSON: {exc}"
        checks[name] = {
            "path": rel,
            "status": status,
            "passed": status == "PASSED",
        }
    return checks


def documentation_checks() -> Dict[str, Any]:
    checks = exists_check(REQUIRED_DOCS)
    stale_hits: List[str] = []
    for rel in STALE_STATUS_FILES:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in STALE_PHRASES:
            if phrase in text:
                stale_hits.append(f"{rel}: contains '{phrase}'")
    readme = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").exists() else ""
    codex = (ROOT / "CODEX.md").read_text(encoding="utf-8") if (ROOT / "CODEX.md").exists() else ""
    milestone_mentions = {
        "readme_mentions_4b_passed": "Milestone 4B: PASSED" in readme,
        "codex_mentions_4c": "Milestone 4C" in codex,
    }
    return {
        "required_docs": checks,
        "stale_status_hits": stale_hits,
        **milestone_mentions,
    }


def main() -> None:
    artifact_checks = exists_check(REQUIRED_ARTIFACTS)
    api_checks = exists_check(REQUIRED_API)
    frontend_checks = exists_check(REQUIRED_FRONTEND)
    validation_checks = report_status_checks()
    doc_checks = documentation_checks()

    blocking_errors: List[str] = []
    warnings: List[str] = []

    for group_name, group in [
        ("artifact", artifact_checks),
        ("api", api_checks),
        ("frontend", frontend_checks),
        ("doc", doc_checks["required_docs"]),
    ]:
        for rel, result in group.items():
            if not result["exists"]:
                blocking_errors.append(f"missing {group_name}: {rel}")

    for name, result in validation_checks.items():
        if not result["passed"]:
            blocking_errors.append(f"validation report not PASSED: {name} ({result['path']}) status={result['status']}")

    if doc_checks["stale_status_hits"]:
        blocking_errors.extend(doc_checks["stale_status_hits"])
    if not doc_checks["readme_mentions_4b_passed"]:
        blocking_errors.append("README.md does not mention Milestone 4B: PASSED")
    if not doc_checks["codex_mentions_4c"]:
        blocking_errors.append("CODEX.md does not mention Milestone 4C")

    frontend_report = ROOT / "data/results/frontend_validation/frontend_validation_report.json"
    if frontend_report.exists():
        payload = read_json(frontend_report)
        npm_build = payload.get("npm_build") or {}
        if payload.get("status") == "PASSED" and npm_build.get("returncode") == 0:
            warnings.extend(payload.get("warnings", []))

    status = "PASSED" if not blocking_errors else "FAILED"
    report = {
        "generated_at": now_iso(),
        "status": status,
        "artifact_checks": artifact_checks,
        "api_checks": api_checks,
        "frontend_checks": frontend_checks,
        "validation_checks": validation_checks,
        "documentation_checks": doc_checks,
        "warnings": warnings,
        "blocking_errors": blocking_errors,
        "demo_commands": [
            "bash scripts/run_full_demo.sh",
            "bash scripts/stop_full_demo.sh",
        ],
        "next_steps": [
            "Capture dashboard screenshots.",
            "Prepare final report and slides.",
            "Do not add new architecture before submission unless fixing a blocker.",
        ],
    }
    write_json(REPORT, report)
    print(f"Final preflight {status}: {len(blocking_errors)} blocking error(s)")
    if blocking_errors:
        raise SystemExit(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
