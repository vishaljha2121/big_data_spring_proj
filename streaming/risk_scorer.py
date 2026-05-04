"""Runtime risk scoring using the published conservative risk config."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple


def bucket_risk(score: float) -> str:
    if score < 0.40:
        return "low"
    if score < 0.70:
        return "medium"
    return "high"


class RuntimeRiskScorer:
    def __init__(self, risk_config: Dict[str, Any]):
        self.config = risk_config
        if self.config.get("fake_labels_used") is not False:
            raise ValueError("risk config must have fake_labels_used=false")

    def score(self, online_features: Dict[str, Any]) -> Dict[str, Any]:
        warnings: List[str] = []
        deviations: List[Tuple[str, float]] = []
        expectations = self.config.get("baseline_expectations", {})
        feature_map = {
            "serve_point_win_pct": "server_point_win_pct_before",
            "return_point_win_pct": "receiver_point_win_pct_before",
        }
        for risk_feature in self.config.get("features_used", []):
            online_name = feature_map.get(risk_feature)
            expected = expectations.get(risk_feature)
            if online_name is None:
                warnings.append(f"{risk_feature} not available from point-event online features")
                continue
            current = online_features.get(online_name)
            if current is None or expected is None:
                warnings.append(f"missing {risk_feature} or baseline expectation")
                continue
            deviations.append((risk_feature, min(1.0, abs(float(current) - float(expected)))))
        if deviations:
            risk_score = max(0.0, min(1.0, sum(value for _, value in deviations) / len(deviations)))
            primary_signal = max(deviations, key=lambda item: item[1])[0]
        else:
            risk_score = 0.0
            primary_signal = "insufficient_online_baseline_features"
        bucket = bucket_risk(risk_score)
        template = self.config["explanation_templates"][bucket]
        return {
            "risk_score": float(risk_score),
            "risk_bucket": bucket,
            "primary_signal": primary_signal,
            "explanation": template.format(primary_signal=primary_signal, risk_score=round(risk_score, 4)),
            "missing_feature_warnings": warnings,
            "fake_labels_used": False,
        }
