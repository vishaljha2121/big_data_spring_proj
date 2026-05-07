import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_kafka_runtime_scripts_exist_and_executable():
    for relative in [
        "scripts/validate_kafka_runtime.py",
        "scripts/run_kafka_replay_smoke.py",
        "scripts/run_streaming_demo.sh",
        "scripts/consume_replay_sample.py",
    ]:
        path = ROOT / relative
        assert path.exists(), relative
        if path.suffix in {".py", ".sh"}:
            assert os.access(path, os.X_OK), relative


def test_topic_config_matches_frozen_contract():
    cfg = json.loads((ROOT / "infra/kafka/topic_config.json").read_text(encoding="utf-8"))
    assert cfg["topic"] == "tennis-point-events"
    assert cfg["partitions"] == 20
    assert cfg["replication_factor"] == 1
    assert cfg["partition_key"] == "synthetic_match_id"
