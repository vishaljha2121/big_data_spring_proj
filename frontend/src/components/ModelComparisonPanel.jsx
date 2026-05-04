import React from "react";
import GlassCard from "./GlassCard.jsx";
import { fixed } from "../utils/formatting.js";

function MetricRow({ label, value }) {
  return (
    <div className="comparison-metric-row">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function ReferenceCard({ title, description, claim, caveat }) {
  return (
    <div className="reference-card">
      <h4>{title}</h4>
      <p>{description}</p>
      <div className="reference-claim">
        <span className="claim-label">Public claim</span>
        <span>{claim}</span>
      </div>
      <small className="reference-caveat">{caveat}</small>
    </div>
  );
}

export default function ModelComparisonPanel({ models, benchmarks }) {
  const oddsLatest = models?.odds_latest || {};
  const odds = models?.odds_metadata_summary || {};
  const evalReport = benchmarks?.eval_report || {};
  const candidate = evalReport?.metrics?.candidate_metrics?.hist_gradient_boosting || {};
  const bench = benchmarks?.scoring_benchmark_report || {};

  const testAuc = candidate.test_auc || odds.test_auc || oddsLatest.test_auc;
  const testBrier = candidate.test_brier_score || odds.test_brier_score || oddsLatest.test_brier_score;
  const throughput = bench.events_per_second;

  return (
    <GlassCard className="comparison-panel" id="comparison">
      <div className="panel-heading compact">
        <div>
          <span className="section-kicker">Context &amp; comparison</span>
          <h2>Model Comparison Context</h2>
          <p>How our point-level model relates to public tennis prediction references.</p>
        </div>
      </div>

      {/* Our model */}
      <div className="comparison-section">
        <h3 className="comparison-section-title">Our Model</h3>
        <div className="comparison-grid">
          <MetricRow label="Target" value="Player A point winner" />
          <MetricRow label="Model" value="HistGradientBoosting classifier" />
          <MetricRow label="Test AUC" value={fixed(testAuc, 4) || "n/a"} />
          <MetricRow label="Test Brier" value={fixed(testBrier, 4) || "n/a"} />
          <MetricRow label="Unit" value="Point-level event prediction" />
          <MetricRow label="Throughput" value={throughput ? `${fixed(throughput, 1)} ev/s` : "n/a"} />
        </div>
      </div>

      {/* Reference benchmarks */}
      <div className="comparison-section">
        <h3 className="comparison-section-title">Public Reference Benchmarks</h3>
        <p className="comparison-note">
          These are public reference points — not validated competitors. Metrics are drawn from
          publicly reported claims and operate at different prediction levels than our model.
        </p>

        <div className="reference-cards">
          <ReferenceCard
            title="TennisBets-style match predictor"
            description="Match-level pre-match model using XGBoost and ELO-style features."
            claim="66.3% held-out match accuracy on 2024 ATP matches"
            caveat="Not directly comparable — match-level accuracy vs our point-level AUC/Brier."
          />
          <ReferenceCard
            title="SportBot-style surface-aware model"
            description="Surface-aware Elo + serve/return analytics for betting outcomes."
            claim="55% recent-pick accuracy, +2% CLV, +9.1% ROI"
            caveat="Betting outcome metrics — not point-level model metrics."
          />
          <ReferenceCard
            title="CourtCruncher-style Elo system"
            description="ATP/Challenger Elo-based betting system emphasizing units and system performance."
            claim="Reported in betting units, not classification accuracy"
            caveat="Not directly comparable to point-level scoring."
          />
        </div>
      </div>

      {/* Verdict */}
      <div className="comparison-verdict">
        <h3>Fair Comparison Verdict</h3>
        <p>
          <strong>Not directly comparable yet.</strong> Our current validated strength is live
          point-level scoring, calibrated probability output, model artifact publication,
          API serving, and demo-ready scoring throughput. A fair head-to-head would require
          building a match-level predictor and evaluating both systems on the same held-out
          match set with the same metric.
        </p>
      </div>

      {/* What would make it comparable */}
      <div className="comparison-future">
        <h4>What would make it comparable?</h4>
        <ul>
          <li>Build match-level outcome labels</li>
          <li>Use the same held-out match set</li>
          <li>Report accuracy, log loss, Brier, and calibration</li>
          <li>Compare against betting odds only if odds data is available</li>
        </ul>
      </div>
    </GlassCard>
  );
}
