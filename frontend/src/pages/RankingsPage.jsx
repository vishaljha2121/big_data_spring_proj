import React from "react";
import Card from "../components/Card.jsx";
import DataTable from "../components/DataTable.jsx";
import { derivePlayers } from "../utils/derivedMetrics.js";
import { pct } from "./pageUtils.jsx";

export default function RankingsPage({ data }) {
  const rows = derivePlayers(data).slice(0, 20).map((player, index) => ({
    key: player.player,
    cells: [index + 1, player.player, player.appearances, player.eventCount, pct(player.avgProbability), player.riskExposure],
  }));
  return (
    <Card title="Sample-Derived Rankings" eyebrow="Not official ATP rankings">
      <p className="module-note">Ranking below is a local demo ordering by scored sample activity. It is not an official ATP ranking.</p>
      <DataTable columns={["Rank", "Player", "Appearances", "Events", "Avg P(A)", "Risk Exposure"]} rows={rows} />
    </Card>
  );
}
