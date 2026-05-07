import React, { useCallback, useEffect, useRef, useState } from "react";
import Card from "../components/Card.jsx";
import ProgressBar from "../components/ProgressBar.jsx";
import { getBenchmarkMetrics, getMatchEvents, getSelectedMatch } from "../utils/derivedMetrics.js";
import { compactReplayId, displayMatchTitle, fixed, pct, risk } from "./pageUtils.jsx";

const SPEED_OPTIONS = [0.5, 1, 2, 5];
const BASE_INTERVAL_MS = 1200;

export default function ReplayCenterPage({ data, onNavigate }) {
  const selected = getSelectedMatch(data);
  const events = getMatchEvents(data);
  const bench = getBenchmarkMetrics(data);

  // ── Playback state ───────────────────────────────────────
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const intervalRef = useRef(null);

  const totalEvents = events.length;
  const currentEvent = events[currentIndex] || null;
  const progressPercent = totalEvents > 0 ? ((currentIndex + 1) / totalEvents) * 100 : 0;

  // ── Interval management ──────────────────────────────────
  const clearPlayback = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (isPlaying && totalEvents > 0) {
      clearPlayback();
      intervalRef.current = setInterval(() => {
        setCurrentIndex((prev) => {
          if (prev >= totalEvents - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, BASE_INTERVAL_MS / playbackSpeed);
    } else {
      clearPlayback();
    }
    return clearPlayback;
  }, [isPlaying, playbackSpeed, totalEvents, clearPlayback]);

  // ── Controls ─────────────────────────────────────────────
  const handlePlayPause = () => setIsPlaying((prev) => !prev);

  const handleStepForward = () => {
    setIsPlaying(false);
    setCurrentIndex((prev) => Math.min(prev + 1, totalEvents - 1));
  };

  const handleStepBack = () => {
    setIsPlaying(false);
    setCurrentIndex((prev) => Math.max(prev - 1, 0));
  };

  const handleRestart = () => {
    setIsPlaying(false);
    setCurrentIndex(0);
  };

  const handleSpeedChange = (speed) => setPlaybackSpeed(speed);

  // Ball marker position based on current index
  const ballLeft = totalEvents > 1 ? (currentIndex / (totalEvents - 1)) * 90 + 5 : 50;
  const ballTop = currentEvent
    ? 30 + ((currentEvent.point_probability_player_a || 0.5) - 0.5) * 40
    : 50;

  return (
    <div className="two-column-page replay-page">
      <div className="page-stack">
        <Card
          title="Historical Match Replay"
          eyebrow="Point-by-point playback"
          action={<button className="link-action" onClick={() => onNavigate("Replay Manifest")}>Manifest →</button>}
        >
          <div className="court-panel">
            <div className="court-meta">
              <div>
                <span className="soft-label">Now replaying</span>
                <h2>{displayMatchTitle(selected)}</h2>
                {compactReplayId(selected?.synthetic_match_id)}
              </div>
              <div>
                <span>Point {currentIndex + 1} of {totalEvents}</span>
                <strong>{totalEvents} total points</strong>
              </div>
            </div>
            <div className="tennis-court">
              <span
                className="ball-marker"
                style={{ left: `${ballLeft}%`, top: `${ballTop}%`, transition: "all 0.3s ease" }}
              />
            </div>
            <ProgressBar value={progressPercent} color="var(--accent)" />
            <div className="replay-controls">
              <button onClick={handleRestart} title="Restart">⏮</button>
              <button onClick={handleStepBack} title="Step −1">⏪</button>
              <button className="primary-action" onClick={handlePlayPause}>
                {isPlaying ? "⏸ Pause" : "▶ Play"}
              </button>
              <button onClick={handleStepForward} title="Step +1">⏩</button>
              <div className="speed-selector">
                {SPEED_OPTIONS.map((s) => (
                  <button
                    key={s}
                    className={playbackSpeed === s ? "active" : ""}
                    onClick={() => handleSpeedChange(s)}
                  >
                    {s}x
                  </button>
                ))}
              </div>
              <button onClick={() => onNavigate("Point Timeline")}>Open Full Timeline</button>
            </div>
          </div>
        </Card>

        {/* Current point detail card */}
        {currentEvent && (
          <Card title="Current Point" eyebrow={`Point #${currentEvent.replay_order ?? currentIndex}`}>
            <div className="current-point-detail">
              <div className="point-stats">
                <p><span className="soft-label">Server</span> <strong>{currentEvent.server_player || "n/a"}</strong></p>
                <p><span className="soft-label">Point Winner</span> <strong>{currentEvent.point_winner_player || "n/a"}</strong></p>
                
                {/* Micro Probability */}
                <p><span className="soft-label">Point P(A)</span> <strong>{pct(currentEvent.point_probability_player_a)}</strong></p>
                
                {/* Macro Probabilities */}
                {currentEvent.game_probability_player_a !== undefined && (
                   <p><span className="soft-label">Game P(A)</span> <strong>{pct(currentEvent.game_probability_player_a)}</strong></p>
                )}
                {currentEvent.set_probability_player_a !== undefined && (
                   <p><span className="soft-label">Set P(A)</span> <strong>{pct(currentEvent.set_probability_player_a)}</strong></p>
                )}
                {currentEvent.match_probability_player_a !== undefined && (
                   <p><span className="soft-label">Match P(A)</span> <strong>{pct(currentEvent.match_probability_player_a)}</strong></p>
                )}
                
                {/* Risk */}
                {risk(currentEvent.risk_bucket, currentEvent.risk_score)}
                <p><span className="soft-label">Risk Signal</span> <strong>{currentEvent.primary_risk_signal || "No signal"}</strong></p>
              </div>
              {currentEvent.outcome_probabilities_available && (
                <div style={{ marginTop: "1rem", fontSize: "0.8rem", color: "var(--light-border)" }}>
                  <em>Note: Game/Set/Match probabilities are statistical estimates and do not represent betting odds or match-win certainty.</em>
                </div>
              )}
            </div>
          </Card>
        )}

        <Card title="Point Event Stream">
          <div className="point-stream">
            {events.map((event, idx) => (
              <article
                key={event.event_id}
                className={idx === currentIndex ? "current-point" : ""}
                onClick={() => { setIsPlaying(false); setCurrentIndex(idx); }}
              >
                <strong>Point #{event.replay_order ?? idx}</strong>
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
            <p><span>Playback speed</span><strong>{playbackSpeed}x</strong></p>
          </div>
        </Card>
        <Card title="Replay Progress">
          <p className="muted-copy">Point-by-point replay of scored match events. Use controls to step through or auto-advance.</p>
          <ProgressBar value={progressPercent} color="var(--green)" />
          <p className="muted-copy" style={{ marginTop: "0.5rem" }}>
            {currentIndex + 1} / {totalEvents} points replayed
          </p>
        </Card>
      </div>
    </div>
  );
}
