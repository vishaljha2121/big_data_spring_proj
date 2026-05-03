import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_courtiq_audit_and_report_exist():
    assert (ROOT / "docs/courtiq_integration_audit.md").exists()
    assert (ROOT / "docs/courtiq_file_inventory.md").exists()
    assert (ROOT / "data/results/courtiq_integration_report.json").exists()


def test_no_courtiq_assets_blindly_copied_to_runtime_paths():
    report = _load_json("data/results/courtiq_integration_report.json")
    runtime_destinations = [
        action["destination"]
        for action in report["merge_actions"]
        if action["destination"].startswith(("scripts/", "producer/", "infra/"))
    ]
    assert runtime_destinations == []
    assert (ROOT / "external_review/courtiq/README.md").exists()


def test_deprecated_architecture_not_reintroduced_as_mandatory():
    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    codex = (ROOT / "CODEX.md").read_text(encoding="utf-8").lower()
    for text in (readme, codex):
        assert "mandatory cassandra" not in text
        assert "mandatory elasticsearch" not in text
        assert "mandatory opensearch" not in text
        assert "mandatory kibana" not in text
        assert "mandatory 50m" not in text
        assert "mandatory 25k events/sec" not in text


def test_no_fake_published_model_latest_files():
    for model_type in ("odds", "risk"):
        latest_path = ROOT / f"data/models/{model_type}/latest.json"
        if not latest_path.exists():
            continue
        latest = json.loads(latest_path.read_text(encoding="utf-8"))
        artifact = ROOT / latest.get("artifact_path", "")
        metadata = ROOT / latest.get("metadata_path", "")
        assert latest.get("status") != "published" or (artifact.exists() and metadata.exists())


def test_parallel_readiness_still_passes():
    result = subprocess.run(
        [".venv/bin/python", "scripts/validate_parallel_readiness.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
