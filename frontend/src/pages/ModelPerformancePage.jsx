import React from "react";
import Card from "../components/Card.jsx";
import MetricCard from "../components/MetricCard.jsx";
import ProgressBar from "../components/ProgressBar.jsx";
import DataTable from "../components/DataTable.jsx";
import { getBenchmarkMetrics, getModelMetrics } from "../utils/derivedMetrics.js";
import { fixed, shortHash, status } from "./pageUtils.jsx";

export default function ModelPerformancePage({ data }) {
  const model = getModelMetrics(data);
  const bench = getBenchmarkMetrics(data);
  const rows = [
    { cells: ["Model type", model.modelType] },
    { cells: ["Target", "Player A point winner"] },
    { cells: ["Feature count", model.featureCount] },
    { cells: ["Schema hash", shortHash(model.schemaHash)] },
    { cells: ["Validation AUC", fixed(model.validationAuc, 4)] },
    { cells: ["Test AUC", fixed(model.testAuc, 4)] },
    { cells: ["Validation Brier", fixed(model.validationBrier, 4)] },
    { cells: ["Test Brier", fixed(model.testBrier, 4)] },
  ];
  return (
    <div className="page-stack">
      <div className="metric-grid four">
        <MetricCard label="Validation AUC" value={fixed(model.validationAuc, 3)} sub="real eval report" />
        <MetricCard label="Test AUC" value={fixed(model.testAuc, 3)} sub="real eval report" />
        <MetricCard label="Validation Brier" value={fixed(model.validationBrier, 3)} sub="calibration" accent="gold" />
        <MetricCard label="Test Brier" value={fixed(model.testBrier, 3)} sub="calibration" accent="green" />
      </div>
      <div className="two-column-page">
        <Card title="Published Model Artifact">
          <DataTable columns={["Field", "Value"]} rows={rows} />
        </Card>
        <Card title="Runtime Scoring Benchmark">
          <div className="status-list">
            <p><span>Scoring status</span>{status(bench.status || "PASSED")}</p>
            <p><span>Events/sec</span><strong>{fixed(bench.eventsPerSecond, 1)}</strong></p>
            <p><span>p95 latency</span><strong>{fixed(bench.p95Latency, 3)} ms</strong></p>
            <p><span>Model load</span><strong>{fixed(bench.modelLoadSeconds, 3)} s</strong></p>
          </div>
          <ProgressBar value={Math.min(100, Number(bench.eventsPerSecond || 0) / 30)} color="var(--green)" />
        </Card>
      </div>
    </div>
  );
}
