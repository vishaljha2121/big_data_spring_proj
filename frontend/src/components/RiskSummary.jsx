import React from "react";
import { bucketClass, fixed } from "../utils/formatting.js";

export default function RiskSummary({ riskSummary, riskEvents }) {
  const counts = riskSummary?.count_by_bucket || riskSummary?.bucket_counts || {};
  const topEvents = riskEvents?.items || riskSummary?.top_risk_events || [];
  return (
    <section className="section">
      <div className="section-header">
        <h2>Risk Summary</h2>
        <p>Risk scores are statistical anomaly signals for review. They are not proof of misconduct or match-fixing.</p>
      </div>
      <div className="risk-grid">
        {["low", "medium", "high"].map((bucket) => (
          <article className={`risk-card ${bucketClass(bucket)}`} key={bucket}>
            <span>{bucket}</span>
            <strong>{counts[bucket] || 0}</strong>
          </article>
        ))}
      </div>
      <h3>Top Risk Events</h3>
      <div className="event-list">
        {topEvents.slice(0, 8).map((event) => (
          <div className="event-row" key={event.event_id}>
            <span>#{event.replay_order}</span>
            <strong>{event.player_a} vs {event.player_b}</strong>
            <span className={`badge ${bucketClass(event.risk_bucket)}`}>{event.risk_bucket} {fixed(event.risk_score, 3)}</span>
            <small>{event.primary_risk_signal}</small>
          </div>
        ))}
      </div>
    </section>
  );
}
