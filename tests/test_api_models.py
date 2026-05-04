from tests.api_test_client import client


def test_current_models_expose_odds_and_risk_metadata():
    response = client.get("/api/models/current")
    assert response.status_code == 200
    payload = response.json()
    assert payload["odds_latest"]["model_type"] == "odds"
    assert payload["risk_latest"]["model_type"] == "risk"
    assert payload["feature_count"] > 0
    assert payload["risk_config_summary"]["fake_labels_used"] is False
