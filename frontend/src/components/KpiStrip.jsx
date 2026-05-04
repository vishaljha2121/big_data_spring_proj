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
  return (
    <section className="kpi-strip" aria-label="System summary KPIs">
      <Kpi label="Scored Events" value={(summary?.scored_event_count || 0).toLocaleString()} detail="validated sample" />
      <Kpi label="Unique Matches" value={(summary?.unique_match_count || 0).toLocaleString()} detail="API-visible" />
      <Kpi label="Odds Model" value={summary?.odds_model_version || "n/a"} detail="published artifact" />
      <Kpi label="Risk Config" value={summary?.risk_model_version || "n/a"} detail="fake_labels_used=false" />
      <Kpi label="Events/sec" value={fixed(summary?.benchmark_events_per_second || bench.events_per_second, 1)} detail="JSONL scoring" />
      <Kpi label="p95 Latency" value={`${fixed(summary?.p95_latency_ms || bench.p95_latency_ms, 3)} ms`} detail="per event" />
    </section>
  );
}
