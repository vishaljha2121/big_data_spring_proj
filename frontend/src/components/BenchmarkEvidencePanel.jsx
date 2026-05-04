import React from "react";
import GlassCard from "./GlassCard.jsx";
import { fixed } from "../utils/formatting.js";

function Metric({ label, value, detail }) {
  return (
    <article className="compact-metric">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{detail}</small>
    </article>
  );
}

export default function BenchmarkEvidencePanel({ benchmarks }) {
  const bench = benchmarks?.scoring_benchmark_report || {};
  const run = benchmarks?.scoring_run_report || {};
  return (
    <GlassCard className="benchmark-panel" id="benchmark">
      <div className="panel-heading compact">
        <div>
          <span className="section-kicker">Runtime evidence</span>
          <h2>Benchmark Evidence</h2>
          <p>Local JSONL scoring benchmark from the validated streaming scorer.</p>
        </div>
      </div>
      <div className="benchmark-grid">
        <Metric label="Events/sec" value={fixed(bench.events_per_second, 1)} detail="throughput" />
        <Metric label="Avg latency" value={`${fixed(bench.average_latency_ms, 3)} ms`} detail="per event" />
        <Metric label="p95 latency" value={`${fixed(bench.p95_latency_ms, 3)} ms`} detail="per event" />
        <Metric label="Model load" value={`${fixed(bench.model_load_time_seconds, 3)} s`} detail="startup" />
        <Metric label="Sample size" value={(run.scored_event_count || bench.events_scored || 0).toLocaleString()} detail="scored events" />
      </div>
    </GlassCard>
  );
}
