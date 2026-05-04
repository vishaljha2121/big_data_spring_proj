import React from "react";
import { fixed } from "../utils/formatting.js";

function Kpi({ label, value, detail }) {
  return (
    <article className="kpi-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </article>
  );
}

export default function KpiStrip({ summary, benchmarks }) {
  const bench = benchmarks?.scoring_benchmark_report || {};
  const evalReport = benchmarks?.eval_report || summary?.eval_report || {};
  const candidate = evalReport?.metrics?.candidate_metrics?.hist_gradient_boosting || {};

  // Prefer test metrics, fall back to validation, then summary-level
  const testAuc = candidate.test_auc || summary?.test_auc || summary?.validation_auc;
  const testBrier = candidate.test_brier_score || summary?.test_brier_score || summary?.validation_brier_score;

  return (
    <section className="kpi-strip" aria-label="System summary KPIs">
      <Kpi
        label="Validated Scored Events"
        value={(summary?.scored_event_count || 0).toLocaleString()}
        detail="local scored sample"
      />
      <Kpi
        label="Matches in Demo"
        value={(summary?.unique_match_count || 0).toLocaleString()}
        detail="API-visible matches"
      />
      <Kpi
        label="Point Model AUC"
        value={fixed(testAuc, 4) || "n/a"}
        detail="held-out point-level AUC"
      />
      <Kpi
        label="Calibration (Brier)"
        value={fixed(testBrier, 4) || "n/a"}
        detail="lower is better"
      />
      <Kpi
        label="Scoring Throughput"
        value={`${fixed(summary?.benchmark_events_per_second || bench.events_per_second, 1)} ev/s`}
        detail="local JSONL benchmark"
      />
      <Kpi
        label="p95 Latency"
        value={`${fixed(summary?.p95_latency_ms || bench.p95_latency_ms, 3)} ms`}
        detail="per event"
      />
    </section>
  );
}
