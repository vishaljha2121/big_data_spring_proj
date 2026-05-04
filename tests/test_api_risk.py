from tests.api_test_client import client


def test_risk_summary_disclaimer_and_events():
    response = client.get("/api/risk/summary")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count_by_bucket"]
    disclaimer = payload["disclaimer"].lower()
    assert "not proof of misconduct" in disclaimer
    assert "not match-fixing detection" in disclaimer
    events = client.get("/api/risk/events?limit=5")
    assert events.status_code == 200
    assert events.json()["items"]
