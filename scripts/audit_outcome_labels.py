#!/usr/bin/env python3
"""Audit outcome labels feasibility for game, set, and match outcomes."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "data/results/outcome_labels"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    print("Loading point features...")
    df_points = pd.read_parquet(ROOT / "data/features/point_features/part-00000.parquet")
    print(f"Loaded {len(df_points)} point features.")
    
    warnings = []
    blocked_reasons = []
    recommended_targets = []
    
    # 1. Match label audit
    match_status = "blocked"
    usable_match_rows = 0
    usable_match_count = 0
    if "label_match_winner_is_player_a" in df_points.columns:
        match_mask = df_points["label_match_winner_is_player_a"].notnull()
        usable_match_rows = match_mask.sum()
        usable_match_count = df_points.loc[match_mask, "match_id"].nunique()
        if usable_match_count > 0:
            match_status = "usable"
            recommended_targets.append("label_player_a_wins_match")
        else:
            blocked_reasons.append("match_winner_is_player_a exists but has no non-null values.")
    else:
        blocked_reasons.append("label_match_winner_is_player_a not found in point_features.")

    # 2. Set label audit
    # We can derive set winner if we group by match_id, set_number and take the final point's point_winner_player?
    # Actually, a better way is to see who won the final game of the set. But wait, if the match ends prematurely, the final set is incomplete.
    # We should only use sets from matches that completed, OR sets that completed (even if the match didn't).
    # Since we don't have a direct 'set_completed' flag, we can rely on matches that have a valid match_winner_player, 
    # and for each match, any set that isn't the final set is definitely completed.
    # The final set is completed if the match has a valid match winner.
    
    # Let's derive set winners where possible.
    print("Deriving set and game outcomes...")
    
    # Filter to matches with a valid match winner
    valid_matches_mask = df_points["label_match_winner_is_player_a"].notnull()
    df_valid_matches = df_points[valid_matches_mask].copy()
    
    # For set winner, group by match_id and set_number. The winner of the set is the winner of the last point of the set.
    # Wait, the last point of a completed set is won by the set winner. 
    set_last_points = df_valid_matches.sort_values("event_index").groupby(["match_id", "set_number"]).tail(1)
    
    # Let's assume the winner of the final point of the set won the set
    set_last_points["set_winner_player"] = set_last_points["point_winner_player"]
    set_last_points["label_player_a_wins_set"] = set_last_points["set_winner_player"] == set_last_points["player_a"]
    
    set_winners = set_last_points[["match_id", "set_number", "label_player_a_wins_set"]]
    df_valid_matches = df_valid_matches.merge(set_winners, on=["match_id", "set_number"], how="left")
    
    set_mask = df_valid_matches["label_player_a_wins_set"].notnull()
    usable_set_rows = set_mask.sum()
    usable_set_count = set_winners.shape[0]
    
    set_status = "blocked"
    if usable_set_count > 0:
        set_status = "usable"
        recommended_targets.append("label_player_a_wins_set")
    else:
        blocked_reasons.append("Could not derive any set winners.")
        
    # For game winner, group by match_id, set_number, game_number.
    game_last_points = df_valid_matches.sort_values("event_index").groupby(["match_id", "set_number", "game_number"]).tail(1)
    game_last_points["game_winner_player"] = game_last_points["point_winner_player"]
    game_last_points["label_player_a_wins_game"] = game_last_points["game_winner_player"] == game_last_points["player_a"]
    
    game_winners = game_last_points[["match_id", "set_number", "game_number", "label_player_a_wins_game"]]
    df_valid_matches = df_valid_matches.merge(game_winners, on=["match_id", "set_number", "game_number"], how="left")
    
    game_mask = df_valid_matches["label_player_a_wins_game"].notnull()
    usable_game_rows = game_mask.sum()
    usable_game_count = game_winners.shape[0]
    
    game_status = "blocked"
    if usable_game_count > 0:
        game_status = "usable"
        recommended_targets.append("label_player_a_wins_game")
    else:
        blocked_reasons.append("Could not derive any game winners.")

    report = {
        "generated_at": now_iso(),
        "match_label_status": match_status,
        "set_label_status": set_status,
        "game_label_status": game_status,
        "usable_match_rows": int(usable_match_rows),
        "usable_set_rows": int(usable_set_rows),
        "usable_game_rows": int(usable_game_rows),
        "usable_match_count": int(usable_match_count),
        "usable_set_count": int(usable_set_count),
        "usable_game_count": int(usable_game_count),
        "blocked_reasons": blocked_reasons,
        "warnings": warnings,
        "recommended_targets": recommended_targets
    }
    
    report_path = RESULTS_DIR / "outcome_label_audit_report.json"
    write_json(report_path, report)
    
    examples = {
        "games": df_valid_matches[["match_id", "set_number", "game_number", "point_number", "label_player_a_wins_game"]].head(10).to_dict(orient="records"),
        "sets": df_valid_matches[["match_id", "set_number", "point_number", "label_player_a_wins_set"]].head(10).to_dict(orient="records"),
        "matches": df_valid_matches[["match_id", "point_number", "label_match_winner_is_player_a"]].head(10).to_dict(orient="records")
    }
    write_json(RESULTS_DIR / "outcome_label_examples.json", examples)
    
    # Also write a doc
    doc_path = ROOT / "docs/outcome_label_derivation_audit.md"
    doc_lines = [
        "# Outcome Label Derivation Audit",
        "",
        f"**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
        "",
        "## Summary",
        f"- Match Label Status: {match_status.upper()}",
        f"- Set Label Status: {set_status.upper()}",
        f"- Game Label Status: {game_status.upper()}",
        "",
        "## Metrics",
        f"- Usable Match Rows: {usable_match_rows} (across {usable_match_count} matches)",
        f"- Usable Set Rows: {usable_set_rows} (across {usable_set_count} sets)",
        f"- Usable Game Rows: {usable_game_rows} (across {usable_game_count} games)",
        "",
        "## Recommended Targets",
        *[f"- {t}" for t in recommended_targets],
        "",
    ]
    doc_lines.extend(["## Blocked Reasons"])
    doc_lines.extend(["- " + b for b in blocked_reasons] if blocked_reasons else ["- None"])
    doc_lines.append("")
    doc_path.write_text("\n".join(doc_lines) + "\n", encoding="utf-8")
    
    print("Audit complete.")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
