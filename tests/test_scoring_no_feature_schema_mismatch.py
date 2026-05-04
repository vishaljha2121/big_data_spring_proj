from pathlib import Path

import pandas as pd

from streaming.model_loader import OddsModelLoader


ROOT = Path(__file__).resolve().parents[1]


def test_scoring_fails_loudly_when_required_feature_missing():
    odds = OddsModelLoader(ROOT / "data/models/odds/latest.json")
    incomplete = pd.DataFrame([{column: 0.0 for column in odds.feature_columns[:-1]}])
    try:
        odds.predict_proba(incomplete)
    except ValueError as exc:
        assert "missing required odds feature columns" in str(exc)
    else:
        raise AssertionError("missing inference feature did not fail")
