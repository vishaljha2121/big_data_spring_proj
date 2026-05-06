import React, { useState } from "react";
import Card from "../components/Card.jsx";
import ProgressBar from "../components/ProgressBar.jsx";
import { getBenchmarkMetrics, getMatchEvents, getSelectedMatch } from "../utils/derivedMetrics.js";
import { compactReplayId, fixed, matchLabel, pct, risk } from "./pageUtils.jsx";

export default function ReplayCenterPage({ data, onNavigate }) {
  const selected = getSelectedMatch(data);
  const events = getMatchEvents(data);
  const bench = getBenchmarkMetrics(data);
  const [playing, setPlaying] = useState(false);
  return (
    <div className="two-column-page replay-page">
      <div className="page-stack">
        <Card title="Historical Match Replay" eyebrow="Local replay dry-run validated" action={<button className="link-action" onClick={() => onNavigate("Replay Manifest")}>Manifest →</button>}>
          <div className="court-panel">
            <div className="court-meta">
              <div>
                <span className="soft-label">Current selected replay</span>
                <h2>{matchLabel(selected)}</h2>
                {compactReplayId(selected?.synthetic_match_id)}
              </div>
              <div>
                <span>Current sample</span>
                <strong>{events.length} points</strong>
              </div>
            </div>
            <div className="tennis-court">
              <span className="ball-marker" />
            </div>
            <div className="replay-controls">
              <button className="primary-action" onClick={() => setPlaying(!playing)}>{playing ? "Pause" : "Play"}</button>
              <button>Step +1 Point</button>
              <button onClick={() => onNavigate("Point Timeline")}>Open Full Timeline</button>
            </div>
          </div>
        </Card>
        <Card title="Point Event Stream">
          <div className="point-stream">
            {events.slice(0, 9).map((event) => (
              <article key={event.event_id}>
                <strong>Point #{event.replay_order}</strong>
                <span>{event.server_player} serving · P(A) {pct(event.point_probability_player_a)}</span>
                {risk(event.risk_bucket, event.risk_score)}
              </article>
            ))}
          </div>
        </Card>
      </div>
      <div className="page-stack">
        <Card title="Replay Summary">
          <div className="status-list">
            <p><span>Replay dry-run</span><strong>Validated</strong></p>
            <p><span>Events scored</span><strong>{(bench.scoredEvents || 0).toLocaleString()}</strong></p>
            <p><span>Throughput</span><strong>{fixed(bench.eventsPerSecond, 1)} events/sec</strong></p>
            <p><span>Kafka runtime</span><strong>Not executed locally</strong></p>
          </div>
        </Card>
        <Card title="Replay Progress">
          <p className="muted-copy">Local demo uses JSONL replay and scorer. Kafka setup exists as scaffold but is not required for final demo.</p>
          <ProgressBar value={100} color="var(--green)" />
        </Card>
      </div>
    </div>
  );
}
