from tests.api_test_client import client


def test_matches_list_and_detail():
    response = client.get("/api/matches?limit=2")
    assert response.status_code == 200
    payload = response.json()
    assert payload["items"]
    match_id = payload["items"][0]["synthetic_match_id"]
    detail = client.get(f"/api/matches/{match_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["summary"]["synthetic_match_id"] == match_id
    assert body["events"]
    events = client.get(f"/api/matches/{match_id}/events?limit=3")
    assert events.status_code == 200
    assert events.json()["count"] <= 3
