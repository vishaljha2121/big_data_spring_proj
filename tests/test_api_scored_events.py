from tests.api_test_client import client


def test_scored_events_list_and_detail():
    response = client.get("/api/scored-events?limit=3&offset=0")
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 3
    assert payload["total_available"] >= 3
    event_id = payload["items"][0]["event_id"]
    detail = client.get(f"/api/scored-events/{event_id}")
    assert detail.status_code == 200
    assert detail.json()["event_id"] == event_id


def test_scored_events_filters_work_for_available_bucket():
    summary = client.get("/api/risk/summary").json()
    bucket = next(bucket for bucket, count in summary["count_by_bucket"].items() if count > 0)
    response = client.get(f"/api/scored-events?risk_bucket={bucket}&limit=5")
    assert response.status_code == 200
    assert all(item["risk_bucket"] == bucket for item in response.json()["items"])
