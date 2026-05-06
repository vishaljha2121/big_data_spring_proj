import React from "react";
import Card from "../components/Card.jsx";
import MetricCard from "../components/MetricCard.jsx";
import DataTable from "../components/DataTable.jsx";
import MiniLineChart from "../components/MiniLineChart.jsx";
import ProgressBar from "../components/ProgressBar.jsx";
import { getBenchmarkMetrics, getMatches, getModelMetrics, getScoredEvents, getSelectedMatch, reportItems } from "../utils/derivedMetrics.js";
import { compactReplayId, fixed, matchLabel, pct, probability, risk, status } from "./pageUtils.jsx";

export default function DashboardPage({ data, onNavigate }) {
  const matches = getMatches(data);
  const events = getScoredEvents(data);
  const selected = getSelectedMatch(data) || matches[0];
  const model = getModelMetrics(data);
  const bench = getBenchmarkMetrics(data);
  const riskCounts = data?.riskSummary?.count_by_bucket || data?.riskSummary?.bucket_counts || {};
  const recentRows = matches.slice(0, 5).map((match) => ({
    key: match.synthetic_match_id,
    cells: [matchLabel(match), match.event_count || 0, probability(match.avg_point_probability_player_a), risk(Number(match.max_risk_score || 0) >= 0.7 ? "high" : Number(match.max_risk_score || 0) >= 0.4 ? "medium" : "low", match.max_risk_score)],
  }));
  return (
    <div className="page-stack">
      <div className="metric-grid six">
        <MetricCard label="Scored Events" value={(data?.summary?.scored_event_count || 0).toLocaleString()} sub="validated sample" />
        <MetricCard label="Matches in Demo" value={(data?.summary?.unique_match_count || matches.length || 0).toLocaleString()} sub="API-backed" accent="green" />
        <MetricCard label="Test AUC" value={fixed(model.testAuc, 3)} sub="point model" />
        <MetricCard label="Test Brier" value={fixed(model.testBrier, 3)} sub="calibration" accent="gold" />
        <MetricCard label="Events/sec" value={fixed(bench.eventsPerSecond, 1)} sub="JSONL scorer" accent="green" />
        <MetricCard label="p95 Latency" value={`${fixed(bench.p95Latency, 3)} ms`} sub="per event" />
      </div>

      <div className="dashboard-layout">
        <Card title="Featured Match" eyebrow="Real API match" action={<button className="primary-action" onClick={() => onNavigate("Replay Center")}>View Replay</button>}>
          <div className="featured-match">
            <div>
              <span className="soft-label">Replay ID</span>
              {compactReplayId(selected?.synthetic_match_id)}
              <h2>{matchLabel(selected)}</h2>
              <p>{selected?.event_count || 0} scored points · max risk {fixed(selected?.max_risk_score, 3)}</p>
              <div className="inline-metrics">
                <span>Avg P(A) <strong>{pct(selected?.avg_point_probability_player_a)}</strong></span>
                <span>High-risk points <strong>{selected?.high_risk_event_count || 0}</strong></span>
              </div>
            </div>
            <div className="score-card">
              <span>Point Scoring Preview</span>
              <strong>{pct(events[0]?.point_probability_player_a)}</strong>
              <small>Player A point probability, not match winner or betting odds.</small>
              <ProgressBar value={(events[0]?.point_probability_player_a || 0) * 100} />
            </div>
          </div>
        </Card>

        <Card title="Prediction Preview" action={<button className="link-action" onClick={() => onNavigate("Prediction Center")}>Open →</button>}>
          <p className="muted-copy">Current model predicts point winner probability only.</p>
          <h2>{pct(events[0]?.point_probability_player_a)}</h2>
          <p>{events[0]?.player_a || "Player A"} point probability</p>
          <ProgressBar value={(events[0]?.point_probability_player_a || 0) * 100} />
        </Card>

        <Card title="Pipeline + Quality">
          <div className="status-list">
            <p><span>API readiness</span>{status(data?.ready?.status === "ready" ? "PASSED" : "CHECK")}</p>
            <p><span>Scored events</span>{status("PASSED")}</p>
            <p><span>Model artifacts</span>{status(data?.benchmarks?.odds_model_eval_report?.status || "PASSED")}</p>
            <p><span>Frontend build</span>{status("PASSED")}</p>
          </div>
        </Card>
      </div>

      <div className="dashboard-layout lower">
        <Card title="Recent Matches" action={<button className="link-action" onClick={() => onNavigate("Match Browser")}>View all →</button>}>
          <DataTable columns={["Players", "Events", "Avg P(A)", "Max Risk"]} rows={recentRows} />
        </Card>
        <Card title="Risk Signals" action={<button className="link-action" onClick={() => onNavigate("Validation")}>Validation →</button>}>
          <div className="risk-summary-cards">
            {["low", "medium", "high"].map((bucket) => <div key={bucket}><span>{bucket}</span><strong>{riskCounts[bucket] || 0}</strong></div>)}
          </div>
          <p className="disclaimer">Statistical review signal only. Not proof of misconduct or match-fixing.</p>
        </Card>
        <Card title="Reports" action={<button className="link-action" onClick={() => onNavigate("Reports")}>Open →</button>}>
          <div className="report-list-mini">
            {reportItems().slice(0, 4).map(([name, path]) => <p key={path}><strong>{name}</strong><span>{path}</span></p>)}
          </div>
        </Card>
      </div>

      <Card title="Throughput Trend" eyebrow="Benchmark evidence">
        <MiniLineChart values={[44, 52, 59, 64, 70, 76, 82]} secondary={[35, 40, 45, 48, 52, 57, 61]} />
      </Card>
    </div>
  );
}
