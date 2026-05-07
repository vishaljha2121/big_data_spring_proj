def extract_api_metrics(store):
    return {
        "status": "up",
        "readiness": store.readiness_checks(),
        "loaded_events": len(store.events),
        "loaded_matches": len(store.events_by_match)
    }

def extract_scoring_metrics(store):
    report = store.scoring_run_report
    return {
        "events_scored": report.get("scored_event_count", 0),
        "average_latency_ms": report.get("average_scoring_latency_ms", 0.0),
        "p95_latency_ms": report.get("p95_scoring_latency_ms", 0.0),
        "invalid_events": report.get("invalid_event_count", 0),
        "feature_schema_hash": report.get("feature_schema_hash", "")
    }

def extract_streaming_metrics(store):
    # Kafka/Spark runtime status. For this local MVP demo, we check validation report
    # or just report NOT_EXECUTED if real Spark/Kafka stream isn't active
    val = store.scoring_validation_report
    if not val:
        return {
            "status": "NOT_EXECUTED",
            "reason": "spark_streaming_validation_report.json not found"
        }
    return {
        "status": "EXECUTED",
        "consumed_events": val.get("consumed_events", 0),
        "scored_events": val.get("scored_events", 0),
        "spark_runtime_status": val.get("spark_runtime_status", "unknown"),
        "kafka_runtime_status": val.get("kafka_runtime_status", "unknown")
    }
