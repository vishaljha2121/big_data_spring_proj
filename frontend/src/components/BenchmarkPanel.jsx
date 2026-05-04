import React from "react";
import { fixed } from "../utils/formatting.js";

export default function BenchmarkPanel({ benchmarks }) {
  const bench = benchmarks?.scoring_benchmark_report || {};
  const run = benchmarks?.scoring_run_report || {};
  return (
    <section className="section">
      <div className="section-header">
        <h2>Benchmark Evidence</h2>
        <p>Local JSONL scoring benchmark from Milestone 3B.</p>
      </div>
      <div className="metric-grid">
        <article className="metric-card"><span>Events/sec</span><strong>{fixed(bench.events_per_second, 1)}</strong><small>throughput</small></article>
        <article className="metric-card"><span>Avg latency</span><strong>{fixed(bench.average_latency_ms, 3)} ms</strong><small>per event</small></article>
        <article className="metric-card"><span>p95 latency</span><strong>{fixed(bench.p95_latency_ms, 3)} ms</strong><small>per event</small></article>
        <article className="metric-card"><span>Model load</span><strong>{fixed(bench.model_load_time_seconds, 3)} s</strong><small>startup</small></article>
        <article className="metric-card"><span>Scored events</span><strong>{run.scored_event_count || bench.events_scored || 0}</strong><small>sample size</small></article>
      </div>
    </section>
  );
}
