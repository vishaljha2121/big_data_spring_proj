import React from "react";
import GlassCard from "./GlassCard.jsx";
import ProbabilityTimeline from "./ProbabilityTimeline.jsx";
import ProbabilityBar from "./ProbabilityBar.jsx";
import RiskBadge from "./RiskBadge.jsx";
import { displayReplayId, hasRealPlayers, fixed, pct, humanizeSignal } from "../utils/formatting.js";

export default function MatchAnalyticsPanel({ matchDetail, matchEvents }) {
  if (!matchDetail) {
    return (
      <GlassCard className="match-analytics">
        <div className="empty-state">Select a match to inspect point probability movement.</div>
      </GlassCard>
    );
  }
  const summary = matchDetail.summary || matchDetail.match || matchDetail;
  const events = matchEvents?.items || matchDetail.events || [];
  const recent = events.slice(0, 7);

  const titleA = summary.player_a || "Player A";
  const titleB = summary.player_b || "Player B";

  return (
    <GlassCard className="match-analytics">
      <div className="panel-heading">
        <div>
          <span className="section-kicker">Primary match analytics</span>
          <h2>{titleA} <span>vs</span> {titleB}</h2>
          <p>Online scoring replay for the selected match.</p>
        </div>
        <code className="id-pill" title={summary.synthetic_match_id}>
          Replay: {displayReplayId(summary.synthetic_match_id)}
        </code>
      </div>

      <div className="match-stat-grid">
        <article><span>Events</span><strong>{summary.event_count || events.length || 0}</strong></article>
        <article><span>Avg P(A)</span><strong>{pct(summary.avg_point_probability_player_a)}</strong></article>
        <article><span>Max risk</span><strong>{fixed(summary.max_risk_score, 3)}</strong></article>
        <article><span>High‑risk events</span><strong>{summary.high_risk_event_count || 0}</strong></article>
      </div>

      <ProbabilityTimeline events={events} />

      <div className="recent-events">
        <div className="mini-heading">
          <h3>Recent Point Events</h3>
          <span>{recent.length} shown</span>
        </div>
        {recent.map((event) => (
          <div className="recent-event-row" key={event.event_id}>
            <span className="order-pill">#{event.replay_order}</span>
            <div>
              <strong>{event.server_player || "Unknown server"}</strong>
              <small>{humanizeSignal(event.primary_risk_signal)}</small>
            </div>
            <ProbabilityBar value={event.point_probability_player_a} label="Player A point probability" />
            <RiskBadge bucket={event.risk_bucket} score={event.risk_score} />
          </div>
        ))}
      </div>
    </GlassCard>
  );
}
