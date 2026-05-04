import React from "react";
import { fixed } from "../utils/formatting.js";

function Card({ label, value, detail }) {
  return (
    <article className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </article>
  );
}

export default function SummaryCards({ summary, benchmarks }) {
  const bench = benchmarks?.scoring_benchmark_report || {};
  return (
    <section className="section">
      <div className="section-header">
        <h2>System Summary</h2>
        <p>Validated local sample served from scored JSONL/Parquet.</p>
      </div>
      <div className="metric-grid">
        <Card label="Scored events" value={(summary?.scored_event_count || 0).toLocaleString()} detail="local scored sample" />
        <Card label="Unique matches" value={(summary?.unique_match_count || 0).toLocaleString()} detail="available in API" />
        <Card label="Odds model" value={summary?.odds_model_version || "n/a"} detail="published artifact" />
        <Card label="Risk config" value={summary?.risk_model_version || "n/a"} detail="fake_labels_used=false" />
        <Card label="Events/sec" value={fixed(summary?.benchmark_events_per_second || bench.events_per_second, 1)} detail="JSONL scoring benchmark" />
        <Card label="p95 latency" value={`${fixed(summary?.p95_latency_ms || bench.p95_latency_ms, 3)} ms`} detail="per event" />
      </div>
    </section>
  );
}
