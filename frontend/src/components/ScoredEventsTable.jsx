import React from "react";
import { bucketClass, fixed, pct } from "../utils/formatting.js";

export default function ScoredEventsTable({ scoredEvents }) {
  const rows = (scoredEvents?.items || []).slice(0, 100);
  return (
    <section className="section">
      <div className="section-header">
        <h2>Scored Events</h2>
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
                <td><code>{event.synthetic_match_id}</code></td>
                <td>{event.player_a} <span className="muted">vs</span> {event.player_b}</td>
                <td>{pct(event.point_probability_player_a)}</td>
                <td>{pct(event.point_probability_player_b)}</td>
                <td><span className={`badge ${bucketClass(event.risk_bucket)}`}>{event.risk_bucket} {fixed(event.risk_score, 3)}</span></td>
                <td>{event.primary_risk_signal}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
