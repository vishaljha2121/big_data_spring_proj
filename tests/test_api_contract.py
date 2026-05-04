from api.app.main import app
from tests.api_test_client import client


def test_openapi_contains_key_endpoints():
    schema = app.openapi()
    paths = schema["paths"]
    for path in [
        "/health",
        "/ready",
        "/api/summary",
        "/api/scored-events",
        "/api/matches",
        "/api/risk/summary",
        "/api/models/current",
        "/api/benchmarks/latest",
    ]:
        assert path in paths


def test_benchmark_endpoint_has_validation_status():
    response = client.get("/api/benchmarks/latest")
    assert response.status_code == 200
    payload = response.json()
    assert payload["validation_status"]["scoring"] == "PASSED"
    assert payload["validation_status"]["benchmark"] == "PASSED"
