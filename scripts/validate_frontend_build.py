#!/usr/bin/env python3
"""Validate the minimal frontend source and run npm build when available."""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
REPORT = ROOT / "data/results/frontend_validation/frontend_validation_report.json"


REQUIRED_FILES = [
    "package.json",
    "index.html",
    "vite.config.js",
    ".env.example",
    "src/main.jsx",
    "src/App.jsx",
    "src/styles.css",
    "src/api/client.js",
    "src/api/types.js",
    "src/theme/surfaceThemes.js",
    "src/components/GlassCard.jsx",
    "src/components/HeroHeader.jsx",
    "src/components/ThemeSwitcher.jsx",
    "src/components/KpiStrip.jsx",
    "src/components/MatchAnalyticsPanel.jsx",
    "src/components/ProbabilityTimeline.jsx",
    "src/components/ProbabilityBar.jsx",
    "src/components/RiskBadge.jsx",
    "src/components/RiskOverviewPanel.jsx",
    "src/components/ModelArtifactPanel.jsx",
    "src/components/BenchmarkEvidencePanel.jsx",
    "src/components/Layout.jsx",
    "src/components/SummaryCards.jsx",
    "src/components/ScoredEventsTable.jsx",
    "src/components/MatchesTable.jsx",
    "src/components/MatchDetail.jsx",
    "src/components/RiskSummary.jsx",
    "src/components/ModelInfo.jsx",
    "src/components/BenchmarkPanel.jsx",
    "src/components/StatusBanner.jsx",
    "src/components/LoadingState.jsx",
    "src/components/ErrorState.jsx",
    "src/pages/DashboardPage.jsx",
    "src/pages/MatchDetailPage.jsx",
    "src/utils/formatting.js",
    "README.md",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_command(command: List[str]) -> Dict[str, Any]:
    result = subprocess.run(command, cwd=FRONTEND, text=True, capture_output=True, timeout=180)
    return {
        "command": " ".join(command),
        "returncode": result.returncode,
        "stdout_tail": result.stdout[-4000:],
        "stderr_tail": result.stderr[-4000:],
    }


def main() -> None:
    errors: List[str] = []
    warnings: List[str] = []
    missing = [path for path in REQUIRED_FILES if not (FRONTEND / path).exists()]
    if missing:
        errors.extend([f"missing frontend/{path}" for path in missing])
    node_path = shutil.which("node")
    npm_path = shutil.which("npm")
    build_result = None
    install_result = None
    if not node_path or not npm_path:
        warnings.append("Node/npm unavailable; frontend build not executed.")
    elif not errors:
        if not (FRONTEND / "node_modules").exists():
            install_result = run_command(["npm", "install"])
            if install_result["returncode"] != 0:
                errors.append("npm install failed")
        if not errors:
            build_result = run_command(["npm", "run", "build"])
            if build_result["returncode"] != 0:
                errors.append("npm run build failed")
    report = {
        "generated_at": now_iso(),
        "status": "PASSED" if not errors and build_result else ("PARTIAL" if not errors else "FAILED"),
        "frontend_dir": str(FRONTEND),
        "required_files_present": not missing,
        "missing_files": missing,
        "node_available": bool(node_path),
        "npm_available": bool(npm_path),
        "node_path": node_path,
        "npm_path": npm_path,
        "npm_install": install_result,
        "npm_build": build_result,
        "warnings": warnings,
        "blocking_errors": errors,
    }
    write_json(REPORT, report)
    if errors:
        raise SystemExit(json.dumps(report, indent=2))
    print(f"Frontend validation {report['status']}")


if __name__ == "__main__":
    main()
