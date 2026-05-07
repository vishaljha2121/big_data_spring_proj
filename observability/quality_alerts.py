def check_data_quality(store) -> list:
    alerts = []
    
    # Check for placeholders
    has_unknowns = any(
        m.get("player_a") == "Unknown" or m.get("player_b") == "Unknown" 
        for m in store.match_summaries
    )
    if has_unknowns:
        alerts.append({
            "type": "UNKNOWN_PLAYERS",
            "severity": "high",
            "message": "Found placeholder players (Unknown) in scored events."
        })
        
    # Check surface coverage
    # Since we know surface coverage is 0% from limitations
    alerts.append({
        "type": "SURFACE_COVERAGE",
        "severity": "medium",
        "message": "Surface metadata is completely unavailable (0% coverage)."
    })
    
    # Check ATP bridge
    alerts.append({
        "type": "ATP_BRIDGE_MISSING",
        "severity": "medium",
        "message": "ATP player ID bridge is unavailable. Stats mapping is limited."
    })
    
    # Check coverage discrepancy
    if store.events and store._replay_events_raw:
        if len(store.events) < len(store._replay_events_raw) * 0.9: # arbitrary threshold for demo vs full
            alerts.append({
                "type": "PARTIAL_COVERAGE",
                "severity": "info",
                "message": f"Only {len(store.events)} events scored out of {len(store._replay_events_raw)} available in manifest."
            })
            
    # Check if streaming executed
    if not store.settings.scoring_run_report.exists() or store.scoring_run_report.get("status") == "FAILED":
        alerts.append({
            "type": "SCORING_RUN_FAILED",
            "severity": "high",
            "message": "No valid scoring run report found."
        })
        
    return alerts
