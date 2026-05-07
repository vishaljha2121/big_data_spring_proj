"""Tests for /api/replay/matches and /api/replay/matches/{id}/events endpoints."""

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


def test_replay_matches_endpoint_exists(client):
    response = client.get("/api/replay/matches?limit=5")
    assert response.status_code == 200


def test_replay_matches_has_items(client):
    data = client.get("/api/replay/matches?limit=5").json()
    assert "items" in data
    assert "total_available" in data


def test_replay_matches_return_player_names(client):
    data = client.get("/api/replay/matches?limit=5").json()
    if data["items"]:
        item = data["items"][0]
        assert "player_a" in item
        assert "player_b" in item
        assert "primary_match_label" in item
        assert "replay_id" in item
        assert "replay_event_count" in item
        assert "scored_available" in item


def test_replay_match_events_chronological(client):
    data = client.get("/api/replay/matches?limit=1").json()
    if not data["items"]:
        pytest.skip("no replay matches available")
    match_id = data["items"][0]["synthetic_match_id"]
    events = client.get(f"/api/replay/matches/{match_id}/events?limit=20").json()
    assert "items" in events
    if len(events["items"]) > 1:
        orders = [e.get("replay_order", 0) for e in events["items"]]
        assert orders == sorted(orders), "Events should be in chronological order"


def test_replay_match_events_404_for_unknown(client):
    response = client.get("/api/replay/matches/nonexistent_match_id/events")
    assert response.status_code == 404


def test_replay_matches_search(client):
    # Just test that search param doesn't crash
    response = client.get("/api/replay/matches?limit=5&search=federer")
    assert response.status_code == 200
