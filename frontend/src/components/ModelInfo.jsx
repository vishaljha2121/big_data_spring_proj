import React from "react";
import { shortHash } from "../utils/formatting.js";

export default function ModelInfo({ models }) {
  const oddsLatest = models?.odds_latest || {};
  const odds = models?.odds_metadata_summary || {};
  const risk = models?.risk_config_summary || {};
  return (
    <section className="section">
      <div className="section-header">
        <h2>Model Metadata</h2>
        <p>Published local artifacts loaded by the API and streaming scorer.</p>
      </div>
      <div className="model-grid">
        <article>
          <h3>Odds Model</h3>
          <dl className="definition-grid">
            <dt>Version</dt><dd>{odds.version || oddsLatest.version}</dd>
            <dt>Type</dt><dd>{odds.model_type || oddsLatest.model_type}</dd>
            <dt>Target</dt><dd>{odds.target_column}</dd>
            <dt>Features</dt><dd>{models?.feature_count}</dd>
            <dt>Schema hash</dt><dd><code>{shortHash(models?.feature_schema_hash || oddsLatest.feature_schema_hash)}</code></dd>
          </dl>
        </article>
        <article>
          <h3>Risk Config</h3>
          <dl className="definition-grid">
            <dt>Version</dt><dd>{risk.version}</dd>
            <dt>Method</dt><dd>{risk.risk_method}</dd>
            <dt>fake_labels_used</dt><dd>{String(risk.fake_labels_used)}</dd>
            <dt>Features</dt><dd>{(risk.features_used || []).join(", ")}</dd>
          </dl>
        </article>
      </div>
    </section>
  );
}
