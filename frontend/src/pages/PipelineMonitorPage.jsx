import React from "react";
import Card from "../components/Card.jsx";
import MetricCard from "../components/MetricCard.jsx";
import MiniLineChart from "../components/MiniLineChart.jsx";
import { getBenchmarkMetrics } from "../utils/derivedMetrics.js";
import { fixed, status } from "./pageUtils.jsx";

export default function PipelineMonitorPage({ data }) {
  const bench = getBenchmarkMetrics(data);
  const obs = data.observability;

  return (
    <div className="page-stack">
      <div className="metric-grid four">
        <MetricCard label="Events/sec" value={fixed(bench.eventsPerSecond, 1)} sub="local JSONL scorer" />
        <MetricCard label="Avg latency" value={`${fixed(bench.averageLatency, 3)} ms`} sub="per event" accent="green" />
        <MetricCard label="p95 latency" value={`${fixed(bench.p95Latency, 3)} ms`} sub="per event" />
        <MetricCard label="Model load" value={`${fixed(bench.modelLoadSeconds, 3)} s`} sub="startup" accent="gold" />
      </div>
      
      {obs && (
        <div className="two-column-page" style={{ marginTop: "1rem" }}>
          <Card title="Observability Layer">
            <div className="status-list">
              <p><span>API Status</span>{status(obs.api_status === "up" ? "PASSED" : "FAILED")}</p>
              <p><span>Scoring Status</span>{status(obs.scoring_status === "OK" ? "PASSED" : "CHECK")}</p>
              <p><span>Streaming Status</span><strong>{obs.streaming_status}</strong></p>
            </div>
            
            <div style={{ marginTop: "1rem" }}>
              <h4>Model Score Distribution Shift</h4>
              {obs.drift_summary?.status === "available" ? (
                <div className="status-list" style={{ marginTop: "0.5rem" }}>
                   <p><span>Validation Mean</span><strong>{fixed(obs.drift_summary.validation_mean, 3)}</strong></p>
                   <p><span>Scored Mean</span><strong>{fixed(obs.drift_summary.scored_mean, 3)}</strong></p>
                   <p><span>Shift Magnitude</span><strong>{fixed(obs.drift_summary.shift_magnitude, 4)}</strong></p>
                   <p><span>Status</span>{status(obs.drift_summary.shift_warning ? "WARNING" : "OK")}</p>
                </div>
              ) : (
                <p className="muted-copy">Score distribution shift data not available.</p>
              )}
            </div>
          </Card>
          
          <Card title="Data Quality Alerts" accent={obs.active_alerts?.length > 0 ? "gold" : "green"}>
            {obs.active_alerts && obs.active_alerts.length > 0 ? (
               <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                 {obs.active_alerts.map((alert, i) => (
                   <li key={i} style={{ padding: "0.75rem", background: "var(--light-bg)", borderRadius: "4px", borderLeft: alert.severity === "high" ? "3px solid var(--red)" : "3px solid var(--gold)" }}>
                     <strong>[{alert.type}]</strong> {alert.message}
                   </li>
                 ))}
               </ul>
            ) : (
               <p className="muted-copy">No active data quality alerts.</p>
            )}
          </Card>
        </div>
      )}
      
      {!obs && (
        <div className="two-column-page" style={{ marginTop: "1rem" }}>
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
      )}
    </div>
  );
}
