#!/usr/bin/env python3
"""Build outcome training data from point features by joining outcome labels."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "data/features/outcome_targets"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    """Return point-in-time safe features."""
    exclude = {
        "event_id", "match_id", "event_index", "player_a", "player_b", 
        "server_player", "receiver_player", "point_winner_player", 
        "source_file", "schema_version", "label_point_winner_is_player_a",
        "label_server_won_point", "label_match_winner_is_player_a",
        "label_match_winner_player", "label_player_a_wins_game", "label_player_a_wins_set",
        "label_player_a_wins_match"
    }
    return [col for col in df.columns if col not in exclude]


def main() -> None:
    print("Loading point features...")
    df_points = pd.read_parquet(ROOT / "data/features/point_features/part-00000.parquet")
    print(f"Loaded {len(df_points)} rows.")

    valid_matches_mask = df_points["label_match_winner_is_player_a"].notnull()
    df_valid = df_points[valid_matches_mask].copy()

    # Derived set winners
    set_last_points = df_valid.sort_values("event_index").groupby(["match_id", "set_number"]).tail(1)
    set_last_points["label_player_a_wins_set"] = set_last_points["point_winner_player"] == set_last_points["player_a"]
    set_winners = set_last_points[["match_id", "set_number", "label_player_a_wins_set"]]
    
    # Derived game winners
    game_last_points = df_valid.sort_values("event_index").groupby(["match_id", "set_number", "game_number"]).tail(1)
    game_last_points["label_player_a_wins_game"] = game_last_points["point_winner_player"] == game_last_points["player_a"]
    game_winners = game_last_points[["match_id", "set_number", "game_number", "label_player_a_wins_game"]]

    # Merge labels
    df_valid = df_valid.merge(set_winners, on=["match_id", "set_number"], how="left")
    df_valid = df_valid.merge(game_winners, on=["match_id", "set_number", "game_number"], how="left")
    
    # We rename label_match_winner_is_player_a
    df_valid["label_player_a_wins_match"] = df_valid["label_match_winner_is_player_a"]

    feature_cols = get_feature_columns(df_valid)
    
    # Write datasets
    report = {
        "generated_at": now_iso(),
        "targets": {}
    }
    
    for target_name, label_col in [
        ("game", "label_player_a_wins_game"),
        ("set", "label_player_a_wins_set"),
        ("match", "label_player_a_wins_match")
    ]:
        print(f"Building point_to_{target_name}...")
        mask = df_valid[label_col].notnull()
        df_target = df_valid[mask].copy()
        
        # Select features + match_id + the label
        # match_id is needed for grouped cross validation later!
        cols_to_save = feature_cols + ["match_id", label_col]
        df_out = df_target[cols_to_save]
        
        out_dir = RESULTS_DIR / f"point_to_{target_name}"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "part-00000.parquet"
        df_out.to_parquet(out_path, index=False, compression="snappy")
        
        report["targets"][target_name] = {
            "rows": len(df_out),
            "label_col": label_col,
            "positive_class_ratio": float(df_out[label_col].mean()),
            "path": str(out_path.relative_to(ROOT))
        }
        print(f"Saved {len(df_out)} rows to {out_path.relative_to(ROOT)}.")

    write_json(RESULTS_DIR / "outcome_target_build_report.json", report)
    
    # Create schema
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "OutcomeTrainingData",
        "description": "Schema for game, set, and match outcome training datasets.",
        "type": "object",
        "properties": {
            "match_id": {"type": "string"},
            "label_player_a_wins_game": {"type": ["boolean", "null"]},
            "label_player_a_wins_set": {"type": ["boolean", "null"]},
            "label_player_a_wins_match": {"type": ["boolean", "null"]}
        }
    }
    for col in feature_cols:
        schema["properties"][col] = {"type": ["number", "boolean", "null"]}
        
    write_json(ROOT / "contracts/outcome_training_schema.json", schema)
    print("Done.")

if __name__ == "__main__":
    main()
