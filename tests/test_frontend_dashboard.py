import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_frontend_dashboard_files_exist():
    required = [
        "frontend/package.json",
        "frontend/index.html",
        "frontend/src/main.jsx",
        "frontend/src/App.jsx",
        "frontend/src/api/client.js",
        "frontend/src/components/SummaryCards.jsx",
        "frontend/src/components/ScoredEventsTable.jsx",
        "frontend/src/components/MatchesTable.jsx",
        "frontend/src/components/MatchDetail.jsx",
        "frontend/src/components/RiskSummary.jsx",
        "frontend/src/components/ModelInfo.jsx",
        "frontend/src/components/BenchmarkPanel.jsx",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    assert not missing


def test_frontend_uses_documented_api_and_safe_language():
    client = (ROOT / "frontend/src/api/client.js").read_text(encoding="utf-8")
    app_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            ROOT / "frontend/src/components/ScoredEventsTable.jsx",
            ROOT / "frontend/src/components/RiskSummary.jsx",
        ]
    )
    for endpoint in [
        "/health",
        "/ready",
        "/api/summary",
        "/api/scored-events",
        "/api/matches",
        "/api/risk/summary",
        "/api/models/current",
        "/api/benchmarks/latest",
    ]:
        assert endpoint in client
    assert "not betting odds" in app_text
    assert "not proof of misconduct" in app_text
    assert "match-fixing" in app_text


def test_frontend_validation_report_passed():
    report = json.loads(
        (ROOT / "data/results/frontend_validation/frontend_validation_report.json").read_text(encoding="utf-8")
    )
    assert report["status"] == "PASSED"
    assert report["required_files_present"] is True
    assert report["npm_build"]["returncode"] == 0
