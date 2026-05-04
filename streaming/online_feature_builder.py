"""Stateful online feature builder for canonical replay point events."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, List, Tuple


DEFAULTED_FEATURES = [
    "elapsed_seconds_delta_from_prev",
]


@dataclass
class MatchState:
    points_played: int = 0
    player_a_points_won: int = 0
    player_b_points_won: int = 0
    server_points_played: int = 0
    server_points_won: int = 0
    receiver_points_played: int = 0
    receiver_points_won: int = 0
    player_a_aces: int = 0
    player_b_aces: int = 0
    player_a_double_faults: int = 0
    player_b_double_faults: int = 0
    previous_elapsed_seconds: float | None = None
    recent_winners: Deque[str] = field(default_factory=lambda: deque(maxlen=10))


class OnlineFeatureBuilder:
    def __init__(self, feature_columns: List[str]):
        self.feature_columns = feature_columns
        self.states: Dict[str, MatchState] = defaultdict(MatchState)
        self.defaulted_features = [name for name in DEFAULTED_FEATURES if name in feature_columns]
        self.missing_features = [name for name in feature_columns if name not in self.supported_features()]
        if self.missing_features:
            raise ValueError(f"online feature builder cannot produce required features: {self.missing_features}")

    @staticmethod
    def supported_features() -> set:
        return {
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
        }

    @staticmethod
    def _pct(numerator: int, denominator: int) -> float:
        return float(numerator / denominator) if denominator else 0.0

    @staticmethod
    def _recent_pct(winners: Deque[str], player: str, window: int) -> float:
        values = list(winners)[-window:]
        if not values:
            return 0.0
        return float(sum(1 for value in values if value == player) / len(values))

    @staticmethod
    def _to_float(value: Any) -> float | None:
        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    def build_features(self, event: Dict[str, Any]) -> Dict[str, Any]:
        state = self.states[event["synthetic_match_id"]]
        player_a = event["player_a"]
        player_b = event["player_b"]
        server = event.get("server_player")
        receiver = event.get("receiver_player")
        elapsed = self._to_float(event.get("replay_offset_seconds"))
        values = {
            "points_played_before": state.points_played,
            "player_a_points_won_before": state.player_a_points_won,
            "player_b_points_won_before": state.player_b_points_won,
            "player_a_point_win_pct_before": self._pct(state.player_a_points_won, state.points_played),
            "player_b_point_win_pct_before": self._pct(state.player_b_points_won, state.points_played),
            "server_points_played_before": state.server_points_played,
            "server_points_won_before": state.server_points_won,
            "server_point_win_pct_before": self._pct(state.server_points_won, state.server_points_played),
            "receiver_points_played_before": state.receiver_points_played,
            "receiver_points_won_before": state.receiver_points_won,
            "receiver_point_win_pct_before": self._pct(state.receiver_points_won, state.receiver_points_played),
            "player_a_recent_5_win_pct_before": self._recent_pct(state.recent_winners, player_a, 5),
            "player_b_recent_5_win_pct_before": self._recent_pct(state.recent_winners, player_b, 5),
            "player_a_recent_10_win_pct_before": self._recent_pct(state.recent_winners, player_a, 10),
            "player_b_recent_10_win_pct_before": self._recent_pct(state.recent_winners, player_b, 10),
            "player_a_aces_before": state.player_a_aces,
            "player_b_aces_before": state.player_b_aces,
            "player_a_double_faults_before": state.player_a_double_faults,
            "player_b_double_faults_before": state.player_b_double_faults,
            "elapsed_seconds_before": state.previous_elapsed_seconds if state.previous_elapsed_seconds is not None else 0.0,
            "elapsed_seconds_delta_from_prev": (
                elapsed - state.previous_elapsed_seconds
                if elapsed is not None and state.previous_elapsed_seconds is not None
                else 0.0
            ),
            "is_server_player_a": bool(server == player_a),
            "is_receiver_player_a": bool(receiver == player_a),
            "has_valid_point_winner": event.get("point_winner_player") in {player_a, player_b},
            "has_valid_server": server in {player_a, player_b},
            "has_elapsed_seconds": elapsed is not None,
        }
        return {column: values[column] for column in self.feature_columns}

    def update_state(self, event: Dict[str, Any]) -> None:
        state = self.states[event["synthetic_match_id"]]
        player_a = event["player_a"]
        player_b = event["player_b"]
        server = event.get("server_player")
        receiver = event.get("receiver_player")
        winner = event.get("point_winner_player")
        state.points_played += 1
        if winner == player_a:
            state.player_a_points_won += 1
        elif winner == player_b:
            state.player_b_points_won += 1
        if server in {player_a, player_b}:
            state.server_points_played += 1
            if winner == server:
                state.server_points_won += 1
        if receiver in {player_a, player_b}:
            state.receiver_points_played += 1
            if winner == receiver:
                state.receiver_points_won += 1
        if event.get("is_ace") is True:
            if server == player_a:
                state.player_a_aces += 1
            elif server == player_b:
                state.player_b_aces += 1
        if event.get("is_double_fault") is True:
            if server == player_a:
                state.player_a_double_faults += 1
            elif server == player_b:
                state.player_b_double_faults += 1
        if winner in {player_a, player_b}:
            state.recent_winners.append(winner)
        elapsed = self._to_float(event.get("replay_offset_seconds"))
        if elapsed is not None:
            state.previous_elapsed_seconds = elapsed

    def build_then_update(self, event: Dict[str, Any]) -> Dict[str, Any]:
        features = self.build_features(event)
        self.update_state(event)
        return features
