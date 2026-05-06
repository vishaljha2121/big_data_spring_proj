import React from "react";
import Card from "../components/Card.jsx";
import DataTable from "../components/DataTable.jsx";
import MetricCard from "../components/MetricCard.jsx";
import MiniLineChart from "../components/MiniLineChart.jsx";
import { derivePlayers } from "../utils/derivedMetrics.js";
import { pct } from "./pageUtils.jsx";

export default function PlayersPage({ data }) {
  const players = derivePlayers(data);
  const selected = players[0] || {};
  const rows = players.slice(0, 25).map((player) => ({
    key: player.player,
    cells: [player.player, player.appearances, player.eventCount, pct(player.avgProbability), player.riskExposure],
  }));
  return (
    <div className="two-column-page">
      <Card title="Player Directory" eyebrow="Sample-derived, not official ATP profiles">
        <DataTable columns={["Player", "Match Appearances", "Point Events", "Avg P(A)", "Risk Exposure"]} rows={rows} />
      </Card>
      <div className="page-stack">
        <Card title="Sample Player Profile">
          <h2>{selected.player || "No player"}</h2>
          <p className="module-note">Derived from scored local sample only. Not an official ranking or full career profile.</p>
          <div className="metric-grid two">
            <MetricCard label="Appearances" value={selected.appearances || 0} sub="local sample" />
            <MetricCard label="Events" value={selected.eventCount || 0} sub="scored points" accent="green" />
          </div>
        </Card>
        <Card title="Recent Form Proxy">
          <MiniLineChart />
        </Card>
      </div>
    </div>
  );
}
