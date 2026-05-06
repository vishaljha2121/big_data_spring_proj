import React from "react";
import Card from "../components/Card.jsx";
import DataTable from "../components/DataTable.jsx";
import MiniLineChart from "../components/MiniLineChart.jsx";
import { derivePlayers } from "../utils/derivedMetrics.js";
import { pct } from "./pageUtils.jsx";

export default function PlayerComparisonPage({ data }) {
  const [a, b] = derivePlayers(data);
  const rows = [
    { cells: ["Sample appearances", a?.appearances || 0, b?.appearances || 0] },
    { cells: ["Scored events", a?.eventCount || 0, b?.eventCount || 0] },
    { cells: ["Avg point probability proxy", pct(a?.avgProbability), pct(b?.avgProbability)] },
    { cells: ["Risk exposure", a?.riskExposure || 0, b?.riskExposure || 0] },
  ];
  return (
    <div className="page-stack">
      <Card title="Compare Two Players" eyebrow="Sample-derived comparison">
        <p className="module-note">This comparison is derived from the local scored demo sample. It is not official ATP head-to-head data.</p>
      </Card>
      <div className="two-column-page">
        <Card title={`${a?.player || "Player A"} vs ${b?.player || "Player B"}`}>
          <DataTable columns={["Metric", a?.player || "Player A", b?.player || "Player B"]} rows={rows} />
        </Card>
        <Card title="Form Proxy Trend">
          <MiniLineChart />
        </Card>
      </div>
    </div>
  );
}
