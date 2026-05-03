import json
import subprocess
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]


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


def test_parallel_docs_and_contracts_exist():
    assert (ROOT / "docs" / "parallel_workstream_handoff.md").exists()
    assert (ROOT / "docs" / "codex_prompt_milestone_2b.md").exists()
    assert (ROOT / "docs" / "codex_prompt_milestone_3a.md").exists()
    for name in REQUIRED_CONTRACTS:
        assert (ROOT / "contracts" / name).exists(), name


def test_topic_config_matches_contract():
    topic_config = json.loads((ROOT / "infra" / "kafka" / "topic_config.json").read_text())
    schema = json.loads((ROOT / "contracts" / "kafka_topic_config_schema.json").read_text())
    jsonschema.validate(topic_config, schema)
    assert topic_config["topic"] == "tennis-point-events"
    assert topic_config["partition_key"] == "synthetic_match_id"


def test_handoff_mentions_both_branches():
    text = (ROOT / "docs" / "parallel_workstream_handoff.md").read_text()
    assert "feature/milestone-2b-model-artifacts" in text
    assert "feature/milestone-3a-replay-producer" in text


def test_no_latest_json_claims_published_without_artifacts():
    for latest in [ROOT / "data" / "models" / "odds" / "latest.json", ROOT / "data" / "models" / "risk" / "latest.json"]:
        if latest.exists():
            payload = json.loads(latest.read_text())
            if payload.get("status") == "published":
                assert (ROOT / payload["artifact_path"]).exists()


def test_validate_parallel_readiness_script_passes():
    result = subprocess.run(
        [str(ROOT / ".venv" / "bin" / "python"), "scripts/validate_parallel_readiness.py"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads((ROOT / "data" / "results" / "parallel_readiness_report.json").read_text())
    assert report["status"] == "PASSED"
