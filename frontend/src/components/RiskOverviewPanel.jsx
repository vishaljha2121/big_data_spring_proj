import React from "react";
import GlassCard from "./GlassCard.jsx";
import RiskBadge from "./RiskBadge.jsx";
import { displayReplayId, hasRealPlayers, fixed, humanizeSignal } from "../utils/formatting.js";

export default function RiskOverviewPanel({ riskSummary, riskEvents }) {
  const counts = riskSummary?.count_by_bucket || riskSummary?.bucket_counts || {};
  const topEvents = riskEvents?.items || riskSummary?.top_risk_events || [];
  return (
    <GlassCard className="rail-panel" id="risk">
      <div className="panel-heading compact">
        <div>
          <span className="section-kicker">Review signals</span>
          <h2>Risk Summary</h2>
        </div>
      </div>
      <p className="risk-disclaimer">Risk scores are statistical anomaly signals for review. They are not proof of misconduct or match-fixing.</p>
      <div className="risk-count-grid">
        {["low", "medium", "high"].map((bucket) => (
          <article key={bucket} className={`risk-count ${bucket}`}>
            <span>{bucket}</span>
            <strong>{counts[bucket] || 0}</strong>
          </article>
        ))}
      </div>
      <div className="ranked-list">
        {topEvents.slice(0, 6).map((event, index) => (
          <article key={event.event_id} className="ranked-risk-row">
            <span className="rank">#{index + 1}</span>
            <div>
              <strong>
                {hasRealPlayers(event)
                  ? `${event.player_a} vs ${event.player_b}`
                  : displayReplayId(event.synthetic_match_id)
                }
              </strong>
              {hasRealPlayers(event) && (
                <small title={event.synthetic_match_id}>Replay: {displayReplayId(event.synthetic_match_id)}</small>
              )}
              <em>{humanizeSignal(event.primary_risk_signal)}</em>
            </div>
            <RiskBadge bucket={event.risk_bucket} score={event.risk_score} />
          </article>
        ))}
        {!topEvents.length ? <div className="empty-state">No risk events returned by API.</div> : null}
      </div>
    </GlassCard>
  );
}
