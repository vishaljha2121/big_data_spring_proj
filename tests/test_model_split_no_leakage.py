import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_model_splits_are_disjoint_and_nonempty():
    train = set(_load("data/models/splits/train_match_ids.json")["match_ids"])
    validation = set(_load("data/models/splits/validation_match_ids.json")["match_ids"])
    test = set(_load("data/models/splits/test_match_ids.json")["match_ids"])
    assert train and validation and test
    assert train.isdisjoint(validation)
    assert train.isdisjoint(test)
    assert validation.isdisjoint(test)


def test_split_report_has_counts_and_target_distribution():
    report = _load("data/models/splits/split_report.json")
    assert report["leakage_check_passed"] is True
    assert report["train_row_count"] > 0
    assert report["validation_row_count"] > 0
    assert report["test_row_count"] > 0
    assert set(report["target_distributions"]) == {"train", "validation", "test"}
