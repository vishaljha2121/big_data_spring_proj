from tests.api_test_client import client


def test_health_and_readiness():
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    ready = client.get("/ready")
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"
