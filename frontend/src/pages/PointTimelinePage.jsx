import React from "react";
import Card from "../components/Card.jsx";
import DataTable from "../components/DataTable.jsx";
import ProbabilityTimeline from "../components/ProbabilityTimeline.jsx";
import { getMatchEvents, getSelectedMatch } from "../utils/derivedMetrics.js";
import { matchLabel, probability, risk } from "./pageUtils.jsx";

export default function PointTimelinePage({ data }) {
  const events = getMatchEvents(data);
  const selected = getSelectedMatch(data);
  const rows = events.slice(0, 80).map((event) => ({
    key: event.event_id,
    cells: [event.replay_order, event.server_player, event.point_winner_player, probability(event.point_probability_player_a), risk(event.risk_bucket, event.risk_score), event.primary_risk_signal || "No signal"],
  }));
  return (
    <div className="page-stack">
      <Card title="Point Probability Timeline" eyebrow={matchLabel(selected)}>
        <ProbabilityTimeline events={events} />
      </Card>
      <Card title="Chronological Point Events">
        <DataTable columns={["Replay Order", "Server", "Point Winner", "P(A)", "Risk", "Signal"]} rows={rows} />
      </Card>
    </div>
  );
}
