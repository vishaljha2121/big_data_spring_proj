#!/usr/bin/env python3
"""Smoke-test the local API demo path and frontend build output."""

from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data/results/final_demo/full_demo_smoke_report.json"
PORT = 18000


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def get_json(path: str, origin: str | None = None) -> Tuple[int, Dict[str, str], Any]:
    request = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}")
    if origin:
        request.add_header("Origin", origin)
    with urllib.request.urlopen(request, timeout=5) as response:
        headers = {key.lower(): value for key, value in response.headers.items()}
        body = response.read().decode("utf-8")
        return response.status, headers, json.loads(body) if body else None


def wait_for_health(timeout_seconds: int = 45) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            status, _, _ = get_json("/health")
            if status == 200:
                return True
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            time.sleep(1)
    return False


def main() -> None:
    errors: list[str] = []
    warnings: list[str] = []
    checks: Dict[str, Any] = {}
    command = [
        sys.executable,
        str(ROOT / "scripts/run_api.py"),
        "--host",
        "127.0.0.1",
        "--port",
        str(PORT),
    ]
    process = subprocess.Popen(
        command,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        if not wait_for_health():
            errors.append("FastAPI /health did not become ready")
        else:
            for endpoint in ["/health", "/ready", "/api/summary"]:
                try:
                    status, _, payload = get_json(endpoint)
                    checks[endpoint] = {"status_code": status, "payload_keys": sorted(payload.keys()) if isinstance(payload, dict) else []}
                    if status != 200:
                        errors.append(f"{endpoint} returned {status}")
                except Exception as exc:  # pragma: no cover - report detail
                    errors.append(f"{endpoint} failed: {exc}")
            try:
                status, headers, _ = get_json("/api/summary", origin="http://127.0.0.1:5173")
                cors_header = headers.get("access-control-allow-origin")
                checks["cors"] = {"status_code": status, "access_control_allow_origin": cors_header}
                if cors_header not in {"http://127.0.0.1:5173", "*"}:
                    errors.append("CORS header for local frontend origin is missing or unexpected")
            except Exception as exc:  # pragma: no cover - report detail
                errors.append(f"CORS smoke check failed: {exc}")
        frontend_dist = ROOT / "frontend/dist/index.html"
        checks["frontend_dist"] = {"path": str(frontend_dist), "exists": frontend_dist.exists()}
        if not frontend_dist.exists():
            warnings.append("frontend/dist/index.html is absent; run scripts/validate_frontend_build.py or npm run build before demo.")
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
    stdout_tail = ""
    stderr_tail = ""
    if process.stdout:
        stdout_tail = process.stdout.read()[-2000:]
    if process.stderr:
        stderr_tail = process.stderr.read()[-2000:]
    status = "PASSED" if not errors else "FAILED"
    report = {
        "generated_at": now_iso(),
        "status": status,
        "api_command": " ".join(command),
        "checks": checks,
        "warnings": warnings,
        "blocking_errors": errors,
        "api_stdout_tail": stdout_tail,
        "api_stderr_tail": stderr_tail,
    }
    write_json(REPORT, report)
    print(f"Full demo smoke {status}: {len(errors)} blocking error(s)")
    if errors:
        raise SystemExit(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
