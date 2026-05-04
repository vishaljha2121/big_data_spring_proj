"""Model metadata endpoints."""

from fastapi import APIRouter

from api.app.data_loader import get_store


router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("/current")
def current_models():
    store = get_store()
    return {
        "odds_latest": store.odds_latest,
        "odds_metadata_summary": {
            "model_type": store.odds_metadata.get("model_type"),
            "version": store.odds_metadata.get("version"),
            "target_column": store.odds_metadata.get("target_column"),
            "validation_auc": store.odds_metadata.get("validation_auc"),
            "test_auc": store.odds_metadata.get("test_auc"),
            "validation_brier_score": store.odds_metadata.get("validation_brier_score"),
            "test_brier_score": store.odds_metadata.get("test_brier_score"),
        },
        "feature_count": len(store.odds_feature_schema.get("feature_columns", [])),
        "feature_schema_hash": store.odds_feature_schema.get("feature_schema_hash"),
        "risk_latest": store.risk_latest,
        "risk_config_summary": {
            "model_type": store.risk_config.get("model_type"),
            "version": store.risk_config.get("version"),
            "risk_method": store.risk_config.get("risk_method"),
            "features_used": store.risk_config.get("features_used", []),
            "thresholds": store.risk_config.get("thresholds", {}),
            "bucket_rules": store.risk_config.get("bucket_rules", {}),
            "fake_labels_used": store.risk_config.get("fake_labels_used"),
        },
    }
