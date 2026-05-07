import React, { useState } from "react";
import Card from "../components/Card.jsx";
import DataTable from "../components/DataTable.jsx";
import ProbabilityTimeline from "../components/ProbabilityTimeline.jsx";
import { getMatchEvents, getSelectedMatch } from "../utils/derivedMetrics.js";
import { displayMatchTitle, probability, risk } from "./pageUtils.jsx";

const PAGE_SIZE = 100;

export default function PointTimelinePage({ data }) {
  const events = getMatchEvents(data);
  const selected = getSelectedMatch(data);
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);

  const displayedEvents = events.slice(0, visibleCount);
  const hasMore = visibleCount < events.length;

  const rows = displayedEvents.map((event) => ({
    key: event.event_id,
    cells: [event.replay_order, event.server_player, event.point_winner_player, probability(event.point_probability_player_a), risk(event.risk_bucket, event.risk_score), event.primary_risk_signal || "No signal"],
  }));

  return (
    <div className="page-stack">
      <Card title="Point Probability Timeline" eyebrow={displayMatchTitle(selected)}>
        <ProbabilityTimeline events={events} />
      </Card>
      <Card title="Chronological Point Events" eyebrow={`${events.length} total events`}>
        <DataTable columns={["Replay Order", "Server", "Point Winner", "P(A)", "Risk", "Signal"]} rows={rows} />
        {hasMore && (
          <div style={{ textAlign: "center", marginTop: "1rem" }}>
            <button
              className="primary-action"
              onClick={() => setVisibleCount((prev) => Math.min(prev + PAGE_SIZE, events.length))}
            >
              Show more ({events.length - visibleCount} remaining)
            </button>
          </div>
        )}
        {!hasMore && events.length > PAGE_SIZE && (
          <p className="muted-copy" style={{ textAlign: "center", marginTop: "0.5rem" }}>
            All {events.length} events displayed
          </p>
        )}
      </Card>
    </div>
  );
}
