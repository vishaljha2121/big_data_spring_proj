import React from "react";
import { bucketClass, fixed, pct } from "../utils/formatting.js";

function Timeline({ events }) {
  const sample = events.slice(0, 80);
  const points = sample
    .map((event, index) => {
      const x = sample.length <= 1 ? 0 : (index / (sample.length - 1)) * 100;
      const y = 100 - Number(event.point_probability_player_a || 0) * 100;
      return `${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(" ");
  return (
    <svg className="timeline" viewBox="0 0 100 100" preserveAspectRatio="none" role="img" aria-label="Player A point probability timeline">
      <polyline points={points} fill="none" stroke="currentColor" strokeWidth="2" vectorEffect="non-scaling-stroke" />
    </svg>
  );
}

export default function MatchDetail({ matchDetail, matchEvents }) {
  if (!matchDetail) return <section className="section"><h2>Match Detail</h2><p>No match selected.</p></section>;
  const summary = matchDetail.summary || matchDetail.match || matchDetail;
  const events = matchEvents?.items || matchDetail.events || [];
  return (
    <section className="section detail">
      <div className="section-header">
        <h2>Match Detail</h2>
        <p>{summary.player_a} vs {summary.player_b}</p>
      </div>
      <div className="detail-grid">
        <dl className="definition-grid">
          <dt>Match ID</dt><dd><code>{summary.synthetic_match_id}</code></dd>
          <dt>Events</dt><dd>{summary.event_count || events.length}</dd>
          <dt>Avg P(A)</dt><dd>{pct(summary.avg_point_probability_player_a)}</dd>
          <dt>Max risk</dt><dd>{fixed(summary.max_risk_score, 3)}</dd>
          <dt>High-risk events</dt><dd>{summary.high_risk_event_count || 0}</dd>
        </dl>
        <div>
          <h3>Point Probability Timeline</h3>
          <Timeline events={events} />
        </div>
      </div>
      <h3>Top Recent Events</h3>
      <div className="event-list">
        {events.slice(0, 8).map((event) => (
          <div className="event-row" key={event.event_id}>
            <span>#{event.replay_order}</span>
            <strong>{pct(event.point_probability_player_a)}</strong>
            <span className={`badge ${bucketClass(event.risk_bucket)}`}>{event.risk_bucket} {fixed(event.risk_score, 3)}</span>
            <small>{event.primary_risk_signal}</small>
          </div>
        ))}
      </div>
    </section>
  );
}
