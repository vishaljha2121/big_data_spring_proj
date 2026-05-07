"""Spark session factory for local Structured Streaming runs."""

from __future__ import annotations


def create_spark_session(app_name: str = "tennis-spark-streaming-scorer"):
    try:
        from pyspark.sql import SparkSession
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("pyspark is not installed") from exc

    return (
        SparkSession.builder.appName(app_name)
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.ui.enabled", "false")
        .config(
            "spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1",
        )
        .getOrCreate()
    )

