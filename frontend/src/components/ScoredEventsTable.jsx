import React from "react";
import GlassCard from "./GlassCard.jsx";
import ProbabilityBar from "./ProbabilityBar.jsx";
import RiskBadge from "./RiskBadge.jsx";
import { compactId } from "../utils/formatting.js";

export default function ScoredEventsTable({ scoredEvents }) {
  const rows = (scoredEvents?.items || []).slice(0, 100);
  return (
    <GlassCard className="table-card wide" id="events">
      <div className="panel-heading compact">
        <div>
          <span className="section-kicker">Replay output</span>
          <h2>Scored Events</h2>
        </div>
        <p>Point probabilities are current-point estimates. They are not betting odds or match-win probabilities.</p>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Order</th>
              <th>Match</th>
              <th>Players</th>
              <th>Player A</th>
              <th>Player B</th>
              <th>Risk</th>
              <th>Primary signal</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((event) => (
              <tr key={event.event_id}>
                <td>{event.replay_order}</td>
                <td><code className="id-pill" title={event.synthetic_match_id}>{compactId(event.synthetic_match_id)}</code></td>
                <td>{event.player_a} <span className="muted">vs</span> {event.player_b}</td>
                <td><ProbabilityBar value={event.point_probability_player_a} label="Player A point probability" /></td>
                <td><ProbabilityBar value={event.point_probability_player_b} label="Player B point probability" /></td>
                <td><RiskBadge bucket={event.risk_bucket} score={event.risk_score} /></td>
                <td><span className="signal-chip">{event.primary_risk_signal || "none"}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </GlassCard>
  );
}
