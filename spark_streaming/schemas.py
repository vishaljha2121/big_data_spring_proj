"""Schema helpers for Spark Kafka point-event parsing."""

from __future__ import annotations

from pathlib import Path


def point_event_struct_schema(schema_path: Path = Path("contracts/point_event_schema.json")):
    try:
        from pyspark.sql.types import BooleanType, DoubleType, LongType, StringType, StructField, StructType
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("pyspark is not installed") from exc

    nullable_string = StringType()
    return StructType(
        [
            StructField("schema_version", nullable_string, False),
            StructField("replay_session_id", nullable_string, False),
            StructField("synthetic_match_id", nullable_string, False),
            StructField("source_match_id", nullable_string, True),
            StructField("event_id", nullable_string, False),
            StructField("synthetic_event_id", nullable_string, False),
            StructField("event_index", LongType(), False),
            StructField("replay_order", LongType(), False),
            StructField("replay_offset_seconds", DoubleType(), True),
            StructField("event_ts", nullable_string, True),
            StructField("player_a", nullable_string, False),
            StructField("player_b", nullable_string, False),
            StructField("server_player", nullable_string, True),
            StructField("receiver_player", nullable_string, True),
            StructField("point_winner_player", nullable_string, True),
            StructField("set_number", LongType(), True),
            StructField("game_number", LongType(), True),
            StructField("point_number", LongType(), True),
            StructField("p1_score", nullable_string, True),
            StructField("p2_score", nullable_string, True),
            StructField("is_ace", BooleanType(), True),
            StructField("is_double_fault", BooleanType(), True),
            StructField("is_break_point", BooleanType(), True),
            StructField("source_file", nullable_string, True),
        ]
    )

