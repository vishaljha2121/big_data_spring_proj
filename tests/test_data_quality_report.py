import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_KEYS = {
    "generated_at",
    "input_archive",
    "schema_version",
    "total_files_seen",
    "point_files_seen",
    "metadata_files_seen",
    "atp_match_files_seen",
    "raw_point_rows",
    "raw_metadata_rows",
    "raw_atp_match_rows",
    "curated_singles_point_rows",
    "curated_singles_match_count",
    "excluded_doubles_files",
    "excluded_doubles_rows",
    "excluded_mixed_files",
    "excluded_mixed_rows",
    "duplicate_event_id_count",
    "missing_match_id_count",
    "missing_event_id_count",
    "metadata_join_success_count",
    "metadata_join_missing_count",
    "invalid_point_winner_count",
    "invalid_point_server_count",
    "special_point_number_count",
    "missing_elapsed_time_count",
    "missing_rally_length_count",
    "missing_surface_count",
    "quarantined_row_count",
    "warnings",
    "blocking_errors",
}


def test_data_quality_report_shape_and_counts():
    report = json.loads((ROOT / "data" / "cleaned" / "data_quality_report.json").read_text())
    assert REQUIRED_KEYS.issubset(report)
    assert report["blocking_errors"] == []
    for key, value in report.items():
        if key.endswith("_count") or key.endswith("_rows") or key.endswith("_files") or key.endswith("_seen"):
            assert isinstance(value, int)
            assert value >= 0


def test_feature_availability_report_covers_required_features():
    report = json.loads((ROOT / "data" / "cleaned" / "feature_availability_report.json").read_text())
    names = {row["feature_name"] for row in report["features"]}
    assert {
        "serve win features",
        "ace features",
        "double fault features",
        "break point features",
        "rally length features",
        "elapsed time features",
        "player metadata features",
        "surface/tournament features",
        "score context features",
    }.issubset(names)
