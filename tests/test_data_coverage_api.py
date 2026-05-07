"""Tests for /api/data/coverage endpoint."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api.app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_coverage_endpoint_exists(client):
    response = client.get("/api/data/coverage")
    assert response.status_code == 200


def test_coverage_has_required_fields(client):
    data = client.get("/api/data/coverage").json()
    assert "scored_event_count" in data
    assert "scored_match_count" in data
    assert "replay_manifest_event_count" in data
    assert "replay_manifest_match_count" in data
    assert "scored_data_source" in data
    assert "replay_manifest_source" in data
    assert "coverage_mode" in data


def test_replay_manifest_larger_than_scored(client):
    data = client.get("/api/data/coverage").json()
    # Manifest should have far more events/matches than scored sample
    assert data["replay_manifest_event_count"] >= data["scored_event_count"]
    assert data["replay_manifest_match_count"] >= data["scored_match_count"]


def test_coverage_mode_is_explicit(client):
    data = client.get("/api/data/coverage").json()
    assert data["coverage_mode"] in ("sample", "full_demo", "manifest_catalog")
