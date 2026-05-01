import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from data_layer_lib import normalize_code, parse_elapsed_seconds, row_has_invalid_point_number, to_int_nullable


def test_point_winner_and_server_code_normalization():
    assert normalize_code("1") == 1
    assert normalize_code("1.0") == 1
    assert normalize_code("2") == 2
    assert normalize_code("2.0") == 2
    assert normalize_code("0") is None
    assert normalize_code("0.0") is None
    assert normalize_code("") is None
    assert normalize_code("bad") is None


def test_special_point_number_is_not_silently_cast():
    assert to_int_nullable("45") == 45
    assert to_int_nullable("45.0") == 45
    assert row_has_invalid_point_number("0X")
    assert row_has_invalid_point_number("0Y")
    assert row_has_invalid_point_number("45D")


def test_elapsed_time_parsing():
    assert parse_elapsed_seconds("00:00:00") == 0.0
    assert parse_elapsed_seconds("0:01:30") == 90.0
    assert parse_elapsed_seconds("1:02:03") == 3723.0
    assert parse_elapsed_seconds("") is None
    assert parse_elapsed_seconds("not-time") is None
