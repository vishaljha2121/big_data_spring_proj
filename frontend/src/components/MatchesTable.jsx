import React from "react";
import GlassCard from "./GlassCard.jsx";
import ProbabilityBar from "./ProbabilityBar.jsx";
import RiskBadge from "./RiskBadge.jsx";
import { displayMatchTitle, displayReplayId, hasRealPlayers, fixed } from "../utils/formatting.js";

export default function MatchesTable({ matches, selectedMatchId, onSelectMatch }) {
  const rows = matches?.items || [];
  return (
    <GlassCard className="table-card">
      <div className="panel-heading compact">
        <div>
          <span className="section-kicker">Match index</span>
          <h2>Matches</h2>
        </div>
        <p>Select a match to inspect point probability and risk movement.</p>
      </div>
      <div className="table-wrap compact">
        <table>
          <thead>
            <tr>
              <th>Matchup</th>
              <th>Replay ID</th>
              <th>Events</th>
              <th>Avg P(A)</th>
              <th>Max Risk</th>
              <th>High‑Risk Events</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((match) => (
              <tr
                key={match.synthetic_match_id}
                className={match.synthetic_match_id === selectedMatchId ? "selected" : ""}
                onClick={() => onSelectMatch(match.synthetic_match_id)}
              >
                <td>
                  <strong>{hasRealPlayers(match) ? `${match.player_a} vs ${match.player_b}` : displayReplayId(match.synthetic_match_id)}</strong>
                </td>
                <td>
                  <button className="id-pill table-id" title={match.synthetic_match_id} onClick={(e) => { e.stopPropagation(); onSelectMatch(match.synthetic_match_id); }}>
                    {displayReplayId(match.synthetic_match_id)}
                  </button>
                </td>
                <td>{match.event_count}</td>
                <td><ProbabilityBar value={match.avg_point_probability_player_a} label="Average Player A point probability" /></td>
                <td><RiskBadge bucket={Number(match.max_risk_score || 0) >= 0.7 ? "high" : Number(match.max_risk_score || 0) >= 0.4 ? "medium" : "low"} score={match.max_risk_score} /></td>
                <td>{match.high_risk_event_count || 0}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </GlassCard>
  );
}
