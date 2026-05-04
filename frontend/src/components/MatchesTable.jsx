import React from "react";
import { fixed, pct } from "../utils/formatting.js";

export default function MatchesTable({ matches, selectedMatchId, onSelectMatch }) {
  const rows = matches?.items || [];
  return (
    <section className="section">
      <div className="section-header">
        <h2>Matches</h2>
        <p>Select a match to inspect point probability and risk movement.</p>
      </div>
      <div className="table-wrap compact">
        <table>
          <thead>
            <tr>
              <th>Match</th>
              <th>Players</th>
              <th>Events</th>
              <th>Avg P(A)</th>
              <th>Max risk</th>
              <th>High-risk events</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((match) => (
              <tr key={match.synthetic_match_id} className={match.synthetic_match_id === selectedMatchId ? "selected" : ""}>
                <td>
                  <button className="link-button" onClick={() => onSelectMatch(match.synthetic_match_id)}>
                    {match.synthetic_match_id}
                  </button>
                </td>
                <td>{match.player_a} <span className="muted">vs</span> {match.player_b}</td>
                <td>{match.event_count}</td>
                <td>{pct(match.avg_point_probability_player_a)}</td>
                <td>{fixed(match.max_risk_score, 3)}</td>
                <td>{match.high_risk_event_count || 0}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
