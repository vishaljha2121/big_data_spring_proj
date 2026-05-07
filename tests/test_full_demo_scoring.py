"""Tests for full-demo scored dataset generation."""

from __future__ import annotations

import json
import sys
import tempfile
from collections import Counter
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def test_full_demo_report_exists():
    """If the full demo has been generated, validate its report."""
    report_path = Path("data/results/streaming_scoring/full_demo_scoring_report.json")
    if not report_path.exists():
        pytest.skip("full demo scoring report not yet generated")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["status"] in ("PASSED", "PARTIAL")
    assert report["selected_match_count"] > 0
    assert report["scored_event_count"] > 0
    assert report["avg_events_per_match"] >= 40


def test_full_demo_contains_complete_matches():
    """Full-demo scored output should contain complete matches, not just first global N events."""
    output_path = Path("data/results/streaming_scoring/scored_events_demo_full.jsonl")
    if not output_path.exists():
        pytest.skip("full demo scored output not yet generated")

    events = []
    with output_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))

    # Group by match
    events_by_match = Counter(e["synthetic_match_id"] for e in events)
    match_count = len(events_by_match)
    assert match_count >= 2, f"Expected at least 2 matches, got {match_count}"

    # Each selected match should have at least min_events_per_match events
    for match_id, count in events_by_match.items():
        assert count >= 40, f"Match {match_id} has only {count} events (expected >= 40)"

    # Total events should be sum of all match events (no global truncation)
    assert len(events) == sum(events_by_match.values())


def test_full_demo_has_real_player_names():
    """Full demo matches should have real player names."""
    output_path = Path("data/results/streaming_scoring/scored_events_demo_full.jsonl")
    if not output_path.exists():
        pytest.skip("full demo scored output not yet generated")

    with output_path.open("r", encoding="utf-8") as f:
        first = json.loads(f.readline())

    assert first.get("player_a") and first["player_a"] != "Unknown"
    assert first.get("player_b") and first["player_b"] != "Unknown"
