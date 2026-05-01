from pathlib import Path
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_feature_layer import build_point_features_from_points


def _fixture():
    winners = ["Alice", "Bob", "Alice", "Alice", "Bob"]
    servers = ["Alice", "Alice", "Bob", "Bob", "Alice"]
    rows = []
    for i, (winner, server) in enumerate(zip(winners, servers)):
        rows.append(
            {
                "event_id": f"m1_{i}",
                "match_id": "m1",
                "source_match_id": "m1",
                "event_index": i,
                "year": 2026,
                "slam": "test",
                "tournament": "test singles",
                "surface": pd.NA,
                "player_a": "Alice",
                "player_b": "Bob",
                "server_player": server,
                "receiver_player": "Bob" if server == "Alice" else "Alice",
                "point_winner_player": winner,
                "set_number": 1,
                "game_number": 1,
                "point_number": i + 1,
                "p1_score": "0",
                "p2_score": "0",
                "p1_games_won": 0,
                "p2_games_won": 0,
                "rally_length": 4,
                "serve_speed_kmh": 160.0 + i,
                "serve_speed_mph": 100.0,
                "is_ace": i == 0,
                "is_double_fault": False,
                "is_break_point": False,
                "elapsed_seconds": float(i * 10),
                "source_file": "fixture.csv",
                "schema_version": "1.0.0",
                "replay_session_id": pd.NA,
                "synthetic_match_id": pd.NA,
                "event_ts": pd.NaT,
            }
        )
    return pd.DataFrame(rows)


def test_first_row_prior_counts_are_zero():
    features = build_point_features_from_points(_fixture())
    first = features.iloc[0]
    assert first["points_played_before"] == 0
    assert first["player_a_points_won_before"] == 0
    assert first["player_b_points_won_before"] == 0


def test_row_k_prior_counts_include_only_rows_before_k():
    features = build_point_features_from_points(_fixture())
    row3 = features.iloc[3]
    assert row3["points_played_before"] == 3
    assert row3["player_a_points_won_before"] == 2
    assert row3["player_b_points_won_before"] == 1


def test_current_point_winner_not_included_in_current_features():
    features = build_point_features_from_points(_fixture())
    row0 = features.iloc[0]
    row1 = features.iloc[1]
    assert row0["player_a_points_won_before"] == 0
    assert row1["player_a_points_won_before"] == 1
    assert row1["player_b_points_won_before"] == 0
    assert row1["player_b_recent_5_win_pct_before"] == 0.0
