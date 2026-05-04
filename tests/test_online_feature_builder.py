from streaming.online_feature_builder import OnlineFeatureBuilder


FEATURE_COLUMNS = [
    "points_played_before",
    "player_a_points_won_before",
    "player_b_points_won_before",
    "player_a_point_win_pct_before",
    "player_b_point_win_pct_before",
    "server_points_played_before",
    "server_points_won_before",
    "server_point_win_pct_before",
    "receiver_points_played_before",
    "receiver_points_won_before",
    "receiver_point_win_pct_before",
    "player_a_recent_5_win_pct_before",
    "player_b_recent_5_win_pct_before",
    "player_a_recent_10_win_pct_before",
    "player_b_recent_10_win_pct_before",
    "player_a_aces_before",
    "player_b_aces_before",
    "player_a_double_faults_before",
    "player_b_double_faults_before",
    "elapsed_seconds_before",
    "elapsed_seconds_delta_from_prev",
    "is_server_player_a",
    "is_receiver_player_a",
    "has_valid_point_winner",
    "has_valid_server",
    "has_elapsed_seconds",
]


def event(index: int, winner: str, server: str = "Player A"):
    receiver = "Player B" if server == "Player A" else "Player A"
    return {
        "synthetic_match_id": "synthetic_match_test",
        "event_index": index,
        "replay_offset_seconds": float(index * 2),
        "player_a": "Player A",
        "player_b": "Player B",
        "server_player": server,
        "receiver_player": receiver,
        "point_winner_player": winner,
        "is_ace": False,
        "is_double_fault": False,
    }


def test_online_features_use_only_prior_events():
    builder = OnlineFeatureBuilder(FEATURE_COLUMNS)
    first = builder.build_features(event(0, "Player A"))
    assert first["points_played_before"] == 0
    assert first["player_a_points_won_before"] == 0
    assert first["player_b_points_won_before"] == 0

    builder.update_state(event(0, "Player A"))
    second = builder.build_features(event(1, "Player B"))
    assert second["points_played_before"] == 1
    assert second["player_a_points_won_before"] == 1
    assert second["player_b_points_won_before"] == 0
    assert second["player_a_recent_5_win_pct_before"] == 1.0

    builder.update_state(event(1, "Player B"))
    third = builder.build_features(event(2, "Player B"))
    assert third["points_played_before"] == 2
    assert third["player_a_points_won_before"] == 1
    assert third["player_b_points_won_before"] == 1
    assert third["player_b_recent_5_win_pct_before"] == 0.5


def test_online_feature_builder_rejects_unmapped_schema_feature():
    try:
        OnlineFeatureBuilder(["points_played_before", "unsupported_feature"])
    except ValueError as exc:
        assert "unsupported_feature" in str(exc)
    else:
        raise AssertionError("unsupported schema feature did not fail")
