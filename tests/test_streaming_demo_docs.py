from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_streaming_runtime_docs_exist_and_are_honest():
    required = [
        "docs/streaming_gap_analysis.md",
        "docs/kafka_runtime_validation.md",
        "docs/spark_structured_streaming_audit.md",
        "docs/streaming_demo_runbook.md",
    ]
    missing = [path for path in required if not (ROOT / path).exists()]
    assert not missing
    combined = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in required)
    assert "not claim" in combined.lower() or "not claimed" in combined.lower()
    assert "JSONL" in combined
    assert "Spark Structured Streaming" in combined
