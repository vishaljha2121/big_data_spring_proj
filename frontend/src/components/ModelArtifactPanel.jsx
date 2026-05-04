import React from "react";
import GlassCard from "./GlassCard.jsx";
import { shortHash, humanizeKey, humanizeTarget, humanizeModelType, humanizeBooleanLabel } from "../utils/formatting.js";

export default function ModelArtifactPanel({ models }) {
  const oddsLatest = models?.odds_latest || {};
  const odds = models?.odds_metadata_summary || {};
  const risk = models?.risk_config_summary || {};
  const riskFeatures = (risk.features_used || []).slice(0, 6);

  const targetValue = odds.target_column || oddsLatest.target_column || "label_point_winner_is_player_a";
  const modelType = odds.model_type || oddsLatest.model_type || "";
  const fakeLabelValue = risk.fake_labels_used === undefined ? false : risk.fake_labels_used;

  return (
    <GlassCard className="rail-panel" id="model">
      <div className="panel-heading compact">
        <div>
          <span className="section-kicker">Published artifacts</span>
          <h2>Model Metadata</h2>
        </div>
      </div>
      <dl className="artifact-list">
        <dt>Odds version</dt><dd>{odds.version || oddsLatest.version || "n/a"}</dd>
        <dt>Model type</dt><dd>{humanizeModelType(modelType)}</dd>
        <dt>Target</dt><dd>{humanizeTarget(targetValue)}</dd>
        <dt>Feature count</dt><dd>{models?.feature_count || "n/a"}</dd>
        <dt>Schema hash</dt><dd><code>{shortHash(models?.feature_schema_hash || oddsLatest.feature_schema_hash)}</code></dd>
        <dt>Risk config</dt><dd>{risk.version || "v1"}</dd>
        <dt>Risk method</dt><dd>{humanizeKey(risk.risk_method || "baseline_deviation_score_v1")}</dd>
        <dt>Label integrity</dt>
        <dd>
          <span className="truth-chip">
            {humanizeBooleanLabel("fake_labels_used", fakeLabelValue)}
          </span>
        </dd>
      </dl>
      <div className="feature-chip-row">
        {riskFeatures.map((feature) => <span key={feature}>{humanizeKey(feature)}</span>)}
      </div>
    </GlassCard>
  );
}
