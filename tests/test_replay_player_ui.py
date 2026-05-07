"""Structural tests for ReplayCenterPage replay functionality."""

from __future__ import annotations

import re
from pathlib import Path

import pytest


REPLAY_PAGE = Path("frontend/src/pages/ReplayCenterPage.jsx")


@pytest.fixture
def replay_source():
    assert REPLAY_PAGE.exists(), "ReplayCenterPage.jsx not found"
    return REPLAY_PAGE.read_text(encoding="utf-8")


def test_has_current_index_state(replay_source):
    """Replay page must track current point index."""
    assert "currentIndex" in replay_source


def test_has_is_playing_state(replay_source):
    """Replay page must track play/pause state."""
    assert "isPlaying" in replay_source


def test_has_playback_speed_state(replay_source):
    """Replay page must track playback speed."""
    assert "playbackSpeed" in replay_source


def test_has_step_forward_handler(replay_source):
    """Replay page must have a step forward handler."""
    assert "handleStepForward" in replay_source or "StepForward" in replay_source


def test_has_step_back_handler(replay_source):
    """Replay page must have a step back handler."""
    assert "handleStepBack" in replay_source or "StepBack" in replay_source


def test_has_restart_handler(replay_source):
    """Replay page must have a restart handler."""
    assert "handleRestart" in replay_source or "Restart" in replay_source


def test_has_interval_for_auto_advance(replay_source):
    """Replay page must use setInterval or similar for auto-advance."""
    assert "setInterval" in replay_source or "interval" in replay_source.lower()


def test_has_speed_selector(replay_source):
    """Replay page must offer speed options."""
    assert "speed-selector" in replay_source or "SPEED_OPTIONS" in replay_source


def test_does_not_hardcode_first_9_events(replay_source):
    """Replay page must NOT hardcode slice(0, 9) anymore."""
    assert ".slice(0, 9)" not in replay_source


def test_has_progress_tracking(replay_source):
    """Replay page must track progress percentage."""
    assert "progressPercent" in replay_source or "progress" in replay_source.lower()


def test_uses_display_match_title(replay_source):
    """Replay page must use displayMatchTitle for player-name-first labeling."""
    assert "displayMatchTitle" in replay_source
