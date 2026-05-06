import React from "react";
import Card from "../components/Card.jsx";
import MetricCard from "../components/MetricCard.jsx";
import MiniLineChart from "../components/MiniLineChart.jsx";
import { getBenchmarkMetrics } from "../utils/derivedMetrics.js";
import { fixed, status } from "./pageUtils.jsx";

export default function PipelineMonitorPage({ data }) {
  const bench = getBenchmarkMetrics(data);
  return (
    <div className="page-stack">
      <div className="metric-grid four">
        <MetricCard label="Events/sec" value={fixed(bench.eventsPerSecond, 1)} sub="local JSONL scorer" />
        <MetricCard label="Avg latency" value={`${fixed(bench.averageLatency, 3)} ms`} sub="per event" accent="green" />
        <MetricCard label="p95 latency" value={`${fixed(bench.p95Latency, 3)} ms`} sub="per event" />
        <MetricCard label="Model load" value={`${fixed(bench.modelLoadSeconds, 3)} s`} sub="startup" accent="gold" />
      </div>
      <div className="two-column-page">
        <Card title="Pipeline State">
          <div className="status-list">
            <p><span>API readiness</span>{status(data?.ready?.status === "ready" ? "PASSED" : "CHECK")}</p>
            <p><span>Replay dry-run</span>{status("PASSED")}</p>
            <p><span>Streaming scorer</span>{status("PASSED")}</p>
            <p><span>Kafka runtime</span><strong>Scaffold available; not executed locally</strong></p>
          </div>
        </Card>
        <Card title="Throughput Trend">
          <MiniLineChart values={[50, 58, 65, 72, 79, 83, 88]} secondary={[36, 41, 44, 48, 52, 57, 61]} />
        </Card>
      </div>
    </div>
  );
}
