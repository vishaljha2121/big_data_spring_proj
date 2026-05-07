import json
import subprocess
from pathlib import Path

from spark_streaming.kafka_streaming_scorer import score_event_batch
from streaming.stream_scorer import StreamScorer


ROOT = Path(__file__).resolve().parents[1]


def sample_event(index=0):
    return {
        "schema_version": "point_event_v1",
        "replay_session_id": "test-session",
        "synthetic_match_id": "synthetic-test-match",
        "source_match_id": "source-test-match",
        "event_id": f"event-{index}",
        "synthetic_event_id": f"synthetic-event-{index}",
        "event_index": index,
        "replay_order": index,
        "replay_offset_seconds": float(index * 2),
        "event_ts": "2026-01-01T00:00:00Z",
        "player_a": "Player A",
        "player_b": "Player B",
        "server_player": "Player A" if index % 2 == 0 else "Player B",
        "receiver_player": "Player B" if index % 2 == 0 else "Player A",
        "point_winner_player": "Player A" if index % 2 == 0 else "Player B",
        "set_number": 1,
        "game_number": 1,
        "point_number": index + 1,
        "p1_score": "0",
        "p2_score": "0",
        "is_ace": False,
        "is_double_fault": False,
        "is_break_point": False,
        "source_file": "synthetic",
    }


def test_spark_output_validator_accepts_small_fixture(tmp_path):
    output_dir = tmp_path / "spark_streaming"
    jsonl_dir = output_dir / "scored_events_jsonl"
    parquet_dir = output_dir / "scored_events_parquet"
    checkpoint_dir = tmp_path / "checkpoint"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    scorer = StreamScorer(ROOT / "data/models/odds/latest.json", ROOT / "data/models/risk/latest.json")
    report = score_event_batch([sample_event(i) for i in range(3)], scorer, jsonl_dir / "part-00000.jsonl", parquet_dir)
    (output_dir / "spark_streaming_run_report.json").write_text(
        json.dumps({"status": "PASSED", "scored_count": report["scored_count"]}),
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            str(ROOT / ".venv/bin/python"),
            str(ROOT / "scripts/validate_spark_streaming_output.py"),
            "--output-dir",
            str(output_dir),
            "--schema",
            str(ROOT / "contracts/scored_event_schema.json"),
            "--expected-count",
            "3",
            "--report",
            str(output_dir / "validation.json"),
            "--checkpoint-dir",
            str(checkpoint_dir),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    validation = json.loads((output_dir / "validation.json").read_text(encoding="utf-8"))
    assert validation["status"] == "PASSED"
