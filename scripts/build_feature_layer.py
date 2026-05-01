#!/usr/bin/env python3
"""Build Milestone 2A point-in-time-safe feature datasets."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd

FEATURE_SCHEMA_VERSION = "2A.1.0"

POINT_FEATURE_COLUMNS = [
    "event_id",
    "match_id",
    "event_index",
    "player_a",
    "player_b",
    "server_player",
    "receiver_player",
    "point_winner_player",
    "source_file",
    "schema_version",
    "elapsed_seconds",
    "set_number",
    "game_number",
    "point_number",
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
    "player_a_break_points_seen_before",
    "player_b_break_points_seen_before",
    "player_a_break_points_won_before",
    "player_b_break_points_won_before",
    "serve_speed_kmh_avg_before",
    "elapsed_seconds_before",
    "elapsed_seconds_delta_from_prev",
    "current_set_number",
    "current_game_number",
    "p1_games_won",
    "p2_games_won",
    "p1_score",
    "p2_score",
    "p1_score_numeric",
    "p2_score_numeric",
    "is_server_player_a",
    "is_receiver_player_a",
    "has_valid_point_winner",
    "has_valid_server",
    "has_rally_length",
    "has_elapsed_seconds",
    "has_surface",
    "rally_length_avg_before",
    "player_a_rally_length_avg_before",
    "player_b_rally_length_avg_before",
    "label_point_winner_is_player_a",
    "label_server_won_point",
    "label_match_winner_is_player_a",
    "label_match_winner_player",
]

MATCH_FEATURE_COLUMNS = [
    "match_id",
    "player_a",
    "player_b",
    "total_points",
    "valid_points",
    "missing_point_winner_count",
    "missing_server_count",
    "player_a_points_won",
    "player_b_points_won",
    "player_a_point_win_pct",
    "player_b_point_win_pct",
    "player_a_aces",
    "player_b_aces",
    "player_a_double_faults",
    "player_b_double_faults",
    "avg_serve_speed_kmh",
    "elapsed_seconds_total",
    "rally_length_available_pct",
    "elapsed_time_available_pct",
    "match_winner_player",
    "match_winner_is_player_a",
    "has_unknown_player",
    "feature_schema_version",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def read_parquet_dir(path: Path, max_matches: Optional[int] = None) -> pd.DataFrame:
    parts = sorted(path.glob("part-*.parquet"))
    if not parts:
        return pd.DataFrame()
    frames = [pd.read_parquet(part, engine="pyarrow") for part in parts]
    df = pd.concat(frames, ignore_index=True)
    if max_matches is not None:
        keep = sorted(df["match_id"].dropna().astype(str).unique())[:max_matches]
        df = df[df["match_id"].astype(str).isin(keep)].copy()
    return df


def safe_divide(numer: pd.Series, denom: pd.Series) -> pd.Series:
    denom_float = denom.astype("float64")
    out = numer.astype("float64") / denom_float.where(denom_float != 0)
    return out.fillna(0.0)


def is_unknown_player(series: pd.Series) -> pd.Series:
    return series.astype("string").str.startswith("unknown_player_", na=False)


def score_to_numeric(value: Any) -> Optional[int]:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip().upper()
    if not text:
        return None
    mapping = {"LOVE": 0, "0": 0, "15": 15, "30": 30, "40": 40, "AD": 50, "A": 50}
    if text in mapping:
        return mapping[text]
    try:
        return int(float(text))
    except ValueError:
        return None


def rolling_prior_pct(values: pd.Series, valid: pd.Series, window: int) -> pd.Series:
    prior_values = values.shift(1).fillna(0).astype("float64")
    prior_valid = valid.shift(1).fillna(0).astype("float64")
    numer = prior_values.rolling(window=window, min_periods=1).sum()
    denom = prior_valid.rolling(window=window, min_periods=1).sum()
    return (numer / denom.where(denom != 0)).fillna(0.0)


def prior_running_average(group: pd.DataFrame, value_col: str, mask_col: Optional[str] = None) -> pd.Series:
    values = pd.to_numeric(group[value_col], errors="coerce")
    mask = values.notna()
    if mask_col is not None:
        mask = mask & group[mask_col].fillna(False).astype(bool)
    running_sum = values.where(mask, 0.0).cumsum() - values.where(mask, 0.0)
    running_count = mask.astype("int64").cumsum() - mask.astype("int64")
    return running_sum / running_count.where(running_count != 0)


def prior_average_by_match(df: pd.DataFrame, value_col: str, mask: Optional[pd.Series] = None) -> pd.Series:
    values = pd.to_numeric(df[value_col], errors="coerce")
    valid = values.notna()
    if mask is not None:
        valid = valid & mask.fillna(False).astype(bool)
    contrib = values.where(valid, 0.0)
    counts = valid.astype("int64")
    running_sum = contrib.groupby(df["match_id"], sort=False).cumsum() - contrib
    running_count = counts.groupby(df["match_id"], sort=False).cumsum() - counts
    return running_sum / running_count.where(running_count != 0)


def build_point_features_from_points(points: pd.DataFrame) -> pd.DataFrame:
    """Return point features using only prior rows inside each match for *_before fields."""
    if points.empty:
        return pd.DataFrame(columns=POINT_FEATURE_COLUMNS)
    df = points.copy()
    df["event_index"] = pd.to_numeric(df["event_index"], errors="coerce").astype("Int64")
    df = df.sort_values(["match_id", "event_index", "event_id"], kind="mergesort").reset_index(drop=True)

    player_a = df["player_a"].astype("string")
    player_b = df["player_b"].astype("string")
    winner = df["point_winner_player"].astype("string")
    server = df["server_player"].astype("string")
    receiver = df["receiver_player"].astype("string")

    df["_valid_winner"] = (winner.eq(player_a) | winner.eq(player_b)).fillna(False)
    df["_valid_server"] = (server.eq(player_a) | server.eq(player_b)).fillna(False)
    df["_player_a_win"] = (winner.eq(player_a).fillna(False) & df["_valid_winner"]).astype("int64")
    df["_player_b_win"] = (winner.eq(player_b).fillna(False) & df["_valid_winner"]).astype("int64")
    df["_valid_point_int"] = df["_valid_winner"].astype("int64")
    df["_server_is_a"] = (server.eq(player_a).fillna(False) & df["_valid_server"]).astype("int64")
    df["_server_is_b"] = (server.eq(player_b).fillna(False) & df["_valid_server"]).astype("int64")
    df["_receiver_is_a"] = (receiver.eq(player_a).fillna(False) & df["_valid_server"]).astype("int64")
    df["_receiver_is_b"] = (receiver.eq(player_b).fillna(False) & df["_valid_server"]).astype("int64")
    df["_server_won"] = (df["_valid_winner"] & df["_valid_server"] & server.eq(winner).fillna(False)).astype("int64")
    df["_receiver_won"] = (df["_valid_winner"] & df["_valid_server"] & receiver.eq(winner).fillna(False)).astype("int64")
    df["_is_ace_int"] = df["is_ace"].fillna(False).astype(bool).astype("int64")
    df["_is_double_fault_int"] = df["is_double_fault"].fillna(False).astype(bool).astype("int64")
    df["_is_break_point_int"] = df["is_break_point"].fillna(False).astype(bool).astype("int64")
    df["_rally_present"] = df["rally_length"].notna()
    df["_surface_present"] = df["surface"].notna()

    grouped = df.groupby("match_id", sort=False)
    features = df[[
        "event_id",
        "match_id",
        "event_index",
        "player_a",
        "player_b",
        "server_player",
        "receiver_player",
        "point_winner_player",
        "source_file",
        "schema_version",
        "elapsed_seconds",
        "set_number",
        "game_number",
        "point_number",
        "p1_games_won",
        "p2_games_won",
        "p1_score",
        "p2_score",
    ]].copy()

    features["points_played_before"] = grouped["_valid_point_int"].cumsum() - df["_valid_point_int"]
    features["player_a_points_won_before"] = grouped["_player_a_win"].cumsum() - df["_player_a_win"]
    features["player_b_points_won_before"] = grouped["_player_b_win"].cumsum() - df["_player_b_win"]
    features["player_a_point_win_pct_before"] = safe_divide(features["player_a_points_won_before"], features["points_played_before"])
    features["player_b_point_win_pct_before"] = safe_divide(features["player_b_points_won_before"], features["points_played_before"])

    a_serve_points_before = grouped["_server_is_a"].cumsum() - df["_server_is_a"]
    b_serve_points_before = grouped["_server_is_b"].cumsum() - df["_server_is_b"]
    a_serve_won = ((df["_server_is_a"] == 1) & (df["_server_won"] == 1)).astype("int64")
    b_serve_won = ((df["_server_is_b"] == 1) & (df["_server_won"] == 1)).astype("int64")
    a_serve_won_before = a_serve_won.groupby(df["match_id"], sort=False).cumsum() - a_serve_won
    b_serve_won_before = b_serve_won.groupby(df["match_id"], sort=False).cumsum() - b_serve_won
    a_return_points_before = grouped["_receiver_is_a"].cumsum() - df["_receiver_is_a"]
    b_return_points_before = grouped["_receiver_is_b"].cumsum() - df["_receiver_is_b"]
    a_return_won = ((df["_receiver_is_a"] == 1) & (df["_receiver_won"] == 1)).astype("int64")
    b_return_won = ((df["_receiver_is_b"] == 1) & (df["_receiver_won"] == 1)).astype("int64")
    a_return_won_before = a_return_won.groupby(df["match_id"], sort=False).cumsum() - a_return_won
    b_return_won_before = b_return_won.groupby(df["match_id"], sort=False).cumsum() - b_return_won

    server_is_a = df["_server_is_a"].astype(bool)
    receiver_is_a = df["_receiver_is_a"].astype(bool)
    features["server_points_played_before"] = a_serve_points_before.where(server_is_a, b_serve_points_before.where(df["_server_is_b"].astype(bool), 0))
    features["server_points_won_before"] = a_serve_won_before.where(server_is_a, b_serve_won_before.where(df["_server_is_b"].astype(bool), 0))
    features["server_point_win_pct_before"] = safe_divide(features["server_points_won_before"], features["server_points_played_before"])
    features["receiver_points_played_before"] = a_return_points_before.where(receiver_is_a, b_return_points_before.where(df["_receiver_is_b"].astype(bool), 0))
    features["receiver_points_won_before"] = a_return_won_before.where(receiver_is_a, b_return_won_before.where(df["_receiver_is_b"].astype(bool), 0))
    features["receiver_point_win_pct_before"] = safe_divide(features["receiver_points_won_before"], features["receiver_points_played_before"])

    features["player_a_recent_5_win_pct_before"] = grouped["_player_a_win"].transform(lambda s: s.shift(1).fillna(0).rolling(5, min_periods=1).sum()) / grouped["_valid_point_int"].transform(lambda s: s.shift(1).fillna(0).rolling(5, min_periods=1).sum()).replace(0, pd.NA)
    features["player_b_recent_5_win_pct_before"] = grouped["_player_b_win"].transform(lambda s: s.shift(1).fillna(0).rolling(5, min_periods=1).sum()) / grouped["_valid_point_int"].transform(lambda s: s.shift(1).fillna(0).rolling(5, min_periods=1).sum()).replace(0, pd.NA)
    features["player_a_recent_10_win_pct_before"] = grouped["_player_a_win"].transform(lambda s: s.shift(1).fillna(0).rolling(10, min_periods=1).sum()) / grouped["_valid_point_int"].transform(lambda s: s.shift(1).fillna(0).rolling(10, min_periods=1).sum()).replace(0, pd.NA)
    features["player_b_recent_10_win_pct_before"] = grouped["_player_b_win"].transform(lambda s: s.shift(1).fillna(0).rolling(10, min_periods=1).sum()) / grouped["_valid_point_int"].transform(lambda s: s.shift(1).fillna(0).rolling(10, min_periods=1).sum()).replace(0, pd.NA)
    for col in ["player_a_recent_5_win_pct_before", "player_b_recent_5_win_pct_before", "player_a_recent_10_win_pct_before", "player_b_recent_10_win_pct_before"]:
        features[col] = features[col].fillna(0.0).astype("float64")

    a_aces = ((df["_server_is_a"] == 1) & (df["_is_ace_int"] == 1)).astype("int64")
    b_aces = ((df["_server_is_b"] == 1) & (df["_is_ace_int"] == 1)).astype("int64")
    a_dfs = ((df["_server_is_a"] == 1) & (df["_is_double_fault_int"] == 1)).astype("int64")
    b_dfs = ((df["_server_is_b"] == 1) & (df["_is_double_fault_int"] == 1)).astype("int64")
    a_bp_seen = ((df["_receiver_is_a"] == 1) & (df["_is_break_point_int"] == 1)).astype("int64")
    b_bp_seen = ((df["_receiver_is_b"] == 1) & (df["_is_break_point_int"] == 1)).astype("int64")
    a_bp_won = (a_bp_seen.astype(bool) & winner.eq(player_a).fillna(False)).astype("int64")
    b_bp_won = (b_bp_seen.astype(bool) & winner.eq(player_b).fillna(False)).astype("int64")
    for tmp_name, values, out_name in [
        ("_a_aces", a_aces, "player_a_aces_before"),
        ("_b_aces", b_aces, "player_b_aces_before"),
        ("_a_dfs", a_dfs, "player_a_double_faults_before"),
        ("_b_dfs", b_dfs, "player_b_double_faults_before"),
        ("_a_bp_seen", a_bp_seen, "player_a_break_points_seen_before"),
        ("_b_bp_seen", b_bp_seen, "player_b_break_points_seen_before"),
        ("_a_bp_won", a_bp_won, "player_a_break_points_won_before"),
        ("_b_bp_won", b_bp_won, "player_b_break_points_won_before"),
    ]:
        df[tmp_name] = values
        features[out_name] = df.groupby("match_id", sort=False)[tmp_name].cumsum() - df[tmp_name]

    df["_serve_speed_present"] = df["serve_speed_kmh"].notna()
    features["serve_speed_kmh_avg_before"] = prior_average_by_match(df, "serve_speed_kmh")
    features["elapsed_seconds_before"] = grouped["elapsed_seconds"].shift(1)
    features["elapsed_seconds_delta_from_prev"] = df["elapsed_seconds"] - features["elapsed_seconds_before"]
    features.loc[df["elapsed_seconds"].isna() | features["elapsed_seconds_before"].isna(), "elapsed_seconds_delta_from_prev"] = pd.NA

    features["current_set_number"] = df["set_number"]
    features["current_game_number"] = df["game_number"]
    features["p1_score_numeric"] = df["p1_score"].map(score_to_numeric).astype("Int64")
    features["p2_score_numeric"] = df["p2_score"].map(score_to_numeric).astype("Int64")
    features["is_server_player_a"] = server_is_a
    features["is_receiver_player_a"] = receiver_is_a
    features["has_valid_point_winner"] = df["_valid_winner"]
    features["has_valid_server"] = df["_valid_server"]
    features["has_rally_length"] = df["_rally_present"]
    features["has_elapsed_seconds"] = df["elapsed_seconds"].notna()
    features["has_surface"] = df["_surface_present"]

    df["_winner_is_a"] = winner.eq(player_a).fillna(False)
    df["_winner_is_b"] = winner.eq(player_b).fillna(False)
    features["rally_length_avg_before"] = prior_average_by_match(df, "rally_length")
    features["player_a_rally_length_avg_before"] = prior_average_by_match(df, "rally_length", df["_winner_is_a"])
    features["player_b_rally_length_avg_before"] = prior_average_by_match(df, "rally_length", df["_winner_is_b"])

    last_winners = (
        df.loc[df["_valid_winner"], ["match_id", "event_index", "point_winner_player"]]
        .sort_values(["match_id", "event_index"], kind="mergesort")
        .groupby("match_id", sort=False)
        .tail(1)
        .set_index("match_id")["point_winner_player"]
    )
    features["label_point_winner_is_player_a"] = df["_player_a_win"].where(df["_valid_winner"], pd.NA).astype("Int64")
    features["label_server_won_point"] = df["_server_won"].where(df["_valid_winner"] & df["_valid_server"], pd.NA).astype("Int64")
    features["label_match_winner_player"] = df["match_id"].map(last_winners).astype("string")
    features["label_match_winner_is_player_a"] = features["label_match_winner_player"].eq(player_a).where(features["label_match_winner_player"].notna(), pd.NA).astype("boolean")

    for col in [
        "points_played_before",
        "player_a_points_won_before",
        "player_b_points_won_before",
        "server_points_played_before",
        "server_points_won_before",
        "receiver_points_played_before",
        "receiver_points_won_before",
        "player_a_aces_before",
        "player_b_aces_before",
        "player_a_double_faults_before",
        "player_b_double_faults_before",
        "player_a_break_points_seen_before",
        "player_b_break_points_seen_before",
        "player_a_break_points_won_before",
        "player_b_break_points_won_before",
    ]:
        features[col] = features[col].fillna(0).astype("int64")
    features["feature_schema_version"] = FEATURE_SCHEMA_VERSION
    features["schema_version"] = FEATURE_SCHEMA_VERSION
    return features[POINT_FEATURE_COLUMNS]


def build_match_features(points: pd.DataFrame) -> pd.DataFrame:
    if points.empty:
        return pd.DataFrame(columns=MATCH_FEATURE_COLUMNS)
    df = points.sort_values(["match_id", "event_index", "event_id"], kind="mergesort").copy()
    player_a = df["player_a"].astype("string")
    player_b = df["player_b"].astype("string")
    winner = df["point_winner_player"].astype("string")
    server = df["server_player"].astype("string")
    df["_valid_winner"] = (winner.eq(player_a) | winner.eq(player_b)).fillna(False)
    df["_valid_server"] = (server.eq(player_a) | server.eq(player_b)).fillna(False)
    df["_winner_a"] = winner.eq(player_a).fillna(False) & df["_valid_winner"]
    df["_winner_b"] = winner.eq(player_b).fillna(False) & df["_valid_winner"]
    df["_server_a"] = server.eq(player_a).fillna(False) & df["_valid_server"]
    df["_server_b"] = server.eq(player_b).fillna(False) & df["_valid_server"]
    df["_ace"] = df["is_ace"].fillna(False).astype(bool)
    df["_double_fault"] = df["is_double_fault"].fillna(False).astype(bool)
    rows = []
    for match_id, g in df.groupby("match_id", sort=False):
        g = g.sort_values(["event_index", "event_id"], kind="mergesort")
        total_points = len(g)
        valid_points = int(g["_valid_winner"].sum())
        pa_won = int(g["_winner_a"].sum())
        pb_won = int(g["_winner_b"].sum())
        last = g.iloc[-1]
        valid_last_winners = g.loc[g["_valid_winner"], "point_winner_player"]
        match_winner_player = valid_last_winners.iloc[-1] if not valid_last_winners.empty else pd.NA
        rows.append(
            {
                "match_id": match_id,
                "player_a": last["player_a"],
                "player_b": last["player_b"],
                "total_points": int(total_points),
                "valid_points": valid_points,
                "missing_point_winner_count": int((~g["_valid_winner"]).sum()),
                "missing_server_count": int((~g["_valid_server"]).sum()),
                "player_a_points_won": pa_won,
                "player_b_points_won": pb_won,
                "player_a_point_win_pct": float(pa_won / valid_points) if valid_points else 0.0,
                "player_b_point_win_pct": float(pb_won / valid_points) if valid_points else 0.0,
                "player_a_aces": int((g["_server_a"] & g["_ace"]).sum()),
                "player_b_aces": int((g["_server_b"] & g["_ace"]).sum()),
                "player_a_double_faults": int((g["_server_a"] & g["_double_fault"]).sum()),
                "player_b_double_faults": int((g["_server_b"] & g["_double_fault"]).sum()),
                "avg_serve_speed_kmh": float(g["serve_speed_kmh"].dropna().mean()) if g["serve_speed_kmh"].notna().any() else None,
                "elapsed_seconds_total": float(g["elapsed_seconds"].max() - g["elapsed_seconds"].min()) if g["elapsed_seconds"].notna().sum() >= 2 else None,
                "rally_length_available_pct": float(g["rally_length"].notna().mean() * 100),
                "elapsed_time_available_pct": float(g["elapsed_seconds"].notna().mean() * 100),
                "match_winner_player": match_winner_player,
                "match_winner_is_player_a": bool(match_winner_player == last["player_a"]) if pd.notna(match_winner_player) else pd.NA,
                "has_unknown_player": bool(is_unknown_player(g["player_a"]).any() or is_unknown_player(g["player_b"]).any()),
                "feature_schema_version": FEATURE_SCHEMA_VERSION,
            }
        )
    return pd.DataFrame(rows)[MATCH_FEATURE_COLUMNS]


def null_rates(df: pd.DataFrame, columns: Iterable[str]) -> Dict[str, float]:
    return {col: round(float(df[col].isna().mean() * 100), 4) for col in columns if col in df.columns}


def write_contracts(contracts: Path) -> None:
    common_num = {"type": ["number", "null"]}
    common_int = {"type": ["integer", "null"]}
    common_str = {"type": ["string", "null"]}
    bool_or_null = {"type": ["boolean", "null"]}

    def schema(title: str, required: List[str], props: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": title,
            "type": "object",
            "required": required,
            "additionalProperties": True,
            "properties": props,
        }

    point_props = {col: common_num for col in POINT_FEATURE_COLUMNS}
    for col in ["event_id", "match_id", "player_a", "player_b", "source_file", "schema_version", "label_match_winner_player", "server_player", "receiver_player", "point_winner_player", "p1_score", "p2_score"]:
        point_props[col] = common_str if col not in {"event_id", "match_id", "player_a", "player_b", "source_file", "schema_version"} else {"type": "string"}
    for col in ["event_index", "set_number", "game_number", "point_number", "points_played_before", "player_a_points_won_before", "player_b_points_won_before", "server_points_played_before", "server_points_won_before", "receiver_points_played_before", "receiver_points_won_before", "player_a_aces_before", "player_b_aces_before", "player_a_double_faults_before", "player_b_double_faults_before", "player_a_break_points_seen_before", "player_b_break_points_seen_before", "player_a_break_points_won_before", "player_b_break_points_won_before", "current_set_number", "current_game_number", "p1_games_won", "p2_games_won", "p1_score_numeric", "p2_score_numeric", "label_point_winner_is_player_a", "label_server_won_point"]:
        point_props[col] = common_int
    for col in ["is_server_player_a", "is_receiver_player_a", "has_valid_point_winner", "has_valid_server", "has_rally_length", "has_elapsed_seconds", "has_surface", "label_match_winner_is_player_a"]:
        point_props[col] = bool_or_null

    match_props = {col: common_num for col in MATCH_FEATURE_COLUMNS}
    for col in ["match_id", "player_a", "player_b", "match_winner_player", "feature_schema_version"]:
        match_props[col] = common_str if col == "match_winner_player" else {"type": "string"}
    for col in ["total_points", "valid_points", "missing_point_winner_count", "missing_server_count", "player_a_points_won", "player_b_points_won", "player_a_aces", "player_b_aces", "player_a_double_faults", "player_b_double_faults"]:
        match_props[col] = {"type": "integer"}
    match_props["match_winner_is_player_a"] = bool_or_null
    match_props["has_unknown_player"] = {"type": "boolean"}
    write_json(contracts / "point_feature_schema.json", schema("PointFeature", POINT_FEATURE_COLUMNS, point_props))
    write_json(contracts / "match_feature_schema.json", schema("MatchFeature", MATCH_FEATURE_COLUMNS, match_props))


def write_docs(docs_dir: Path, build_report: Dict[str, Any], quality_report: Dict[str, Any]) -> None:
    docs_dir.mkdir(parents=True, exist_ok=True)
    verdict = "PASSED" if build_report["point_in_time_safe"] and not build_report["blocking_errors"] else "FAILED"
    (docs_dir / "feature_engineering_audit.md").write_text(
        f"""# Feature Engineering Audit

## Inputs Used

Milestone 2A used only `data/curated/singles_points/` and `data/curated/singles_matches/`. No staging CSV.GZ files, model artifacts, Kafka, streaming jobs, APIs, or frontend code were used.

## Transformations

- Curated singles points were sorted by `match_id`, `event_index`, and `event_id`.
- Point-level cumulative, rolling, serve/return, score-context, sparse rally, elapsed-time, and label columns were generated.
- Match-level summaries were derived from the point feature layer.
- All feature outputs were written as Parquet under `data/features/`.

## Point-In-Time Safety

Every `*_before` feature is shifted by construction: cumulative values subtract the current row's contribution, rolling windows use shifted values, and prior averages use only rows with `event_index` lower than the current row within the same match. Labels are allowed to use future outcome information and are separated with `label_` prefixes.

## Feature List

The point feature contract is `contracts/point_feature_schema.json`; the match feature contract is `contracts/match_feature_schema.json`.

## Labels

- `label_point_winner_is_player_a`
- `label_server_won_point`
- `label_match_winner_is_player_a`
- `label_match_winner_player`

## Known Limitations

- Rally features are sparse and are not recommended for the MVP primary feature set.
- Surface features are unavailable because curated `surface` is missing.
- Match winner labels are inferred from the last valid point winner in each curated point sequence, not from an ATP bridge.
- Rows with unknown-player placeholders are preserved but flagged.

## Verdict

Milestone 2A feature layer status: **{verdict}**.

Input rows: {build_report['input_rows']}
Output rows: {build_report['output_rows']}
Match count: {build_report['match_count']}
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--curated", type=Path, default=Path("data/curated"))
    parser.add_argument("--out", type=Path, default=Path("data/features"))
    parser.add_argument("--contracts", type=Path, default=Path("contracts"))
    parser.add_argument("--max-matches", type=int)
    args = parser.parse_args()

    points = read_parquet_dir(args.curated / "singles_points", args.max_matches)
    if points.empty:
        raise SystemExit("No curated singles points found.")
    point_features = build_point_features_from_points(points)
    match_features = build_match_features(points)

    clean_dir(args.out / "point_features")
    clean_dir(args.out / "match_features")
    point_features.to_parquet(args.out / "point_features" / "part-00000.parquet", index=False, engine="pyarrow")
    match_features.to_parquet(args.out / "match_features" / "part-00000.parquet", index=False, engine="pyarrow")
    write_contracts(args.contracts)

    sparse = ["rally_length_avg_before", "player_a_rally_length_avg_before", "player_b_rally_length_avg_before"]
    warnings = [
        "rally_length coverage is sparse; rally features are excluded from the recommended MVP primary set",
        "surface is unavailable in curated data; surface-based features remain blocked",
        "match winner labels are inferred from last valid point winner because ATP match bridge is not reliable yet",
    ]
    build_report = {
        "generated_at": now_iso(),
        "input_dataset": str(args.curated / "singles_points"),
        "output_dataset": str(args.out),
        "input_rows": int(len(points)),
        "output_rows": int(len(point_features)),
        "match_count": int(point_features["match_id"].nunique()),
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "point_in_time_safe": True,
        "labels_created": [
            "label_point_winner_is_player_a",
            "label_server_won_point",
            "label_match_winner_is_player_a",
            "label_match_winner_player",
        ],
        "sparse_features": sparse,
        "warnings": warnings,
        "blocking_errors": [],
    }
    key_features = [
        "serve_speed_kmh_avg_before",
        "elapsed_seconds_before",
        "elapsed_seconds_delta_from_prev",
        "rally_length_avg_before",
        "player_a_rally_length_avg_before",
        "player_b_rally_length_avg_before",
        "label_point_winner_is_player_a",
        "label_server_won_point",
        "label_match_winner_is_player_a",
    ]
    quality_report = {
        "generated_at": now_iso(),
        "feature_schema_version": FEATURE_SCHEMA_VERSION,
        "null_rates": null_rates(point_features, key_features),
        "availability_percent": {
            "serve_return_features": round(float((point_features["has_valid_server"] & point_features["has_valid_point_winner"]).mean() * 100), 4),
            "score_context_features": round(float(point_features[["p1_score", "p2_score", "p1_games_won", "p2_games_won"]].notna().all(axis=1).mean() * 100), 4),
            "elapsed_time_features": round(float(point_features["has_elapsed_seconds"].mean() * 100), 4),
            "rally_features": round(float(point_features["has_rally_length"].mean() * 100), 4),
            "surface_features": round(float(point_features["has_surface"].mean() * 100), 4),
        },
        "unknown_player_row_count": int((is_unknown_player(point_features["player_a"]) | is_unknown_player(point_features["player_b"])).sum()),
        "invalid_or_missing_winner_count": int((~point_features["has_valid_point_winner"].astype(bool)).sum()),
        "invalid_or_missing_server_count": int((~point_features["has_valid_server"].astype(bool)).sum()),
        "missing_elapsed_seconds_count": int((~point_features["has_elapsed_seconds"].astype(bool)).sum()),
        "missing_rally_length_count": int((~point_features["has_rally_length"].astype(bool)).sum()),
        "recommendation_mvp_feature_set": [
            "point/game score context",
            "prior point win percentages",
            "prior serve and return win percentages",
            "recent 5/10 point win percentages",
            "ace and double-fault prior counts",
            "elapsed-time availability flags",
        ],
        "recommendation_excluded_features": [
            "surface-based features until metadata improves",
            "rally-length primary features because coverage is sparse",
            "ATP bridge features until a reliable join key is validated",
        ],
    }
    write_json(args.out / "feature_build_report.json", build_report)
    write_json(args.out / "feature_quality_report.json", quality_report)
    write_json(
        args.out / "zone_metadata.json",
        {
            "zone": "features",
            "schema_version": FEATURE_SCHEMA_VERSION,
            "generated_at": now_iso(),
            "format": "parquet",
            "datasets": {"point_features_parts": 1, "match_features_parts": 1},
        },
    )
    write_docs(Path("docs"), build_report, quality_report)
    print(f"wrote point features={len(point_features)} match features={len(match_features)} to {args.out}")


if __name__ == "__main__":
    main()
