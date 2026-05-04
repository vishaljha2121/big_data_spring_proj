import React, { useMemo } from "react";
import { pct } from "../utils/formatting.js";

export default function ProbabilityTimeline({ events }) {
  const rows = (events || []).filter((event) => Number.isFinite(Number(event.point_probability_player_a))).slice(0, 160);
  const geometry = useMemo(() => {
    const width = 960;
    const height = 340;
    const pad = { top: 26, right: 28, bottom: 38, left: 48 };
    const innerW = width - pad.left - pad.right;
    const innerH = height - pad.top - pad.bottom;
    const points = rows.map((event, index) => {
      const x = pad.left + (rows.length <= 1 ? 0 : (index / (rows.length - 1)) * innerW);
      const probability = Math.max(0, Math.min(1, Number(event.point_probability_player_a || 0)));
      const y = pad.top + (1 - probability) * innerH;
      return { x, y, probability, event };
    });
    const path = points.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x.toFixed(1)} ${point.y.toFixed(1)}`).join(" ");
    return { width, height, pad, innerW, innerH, points, path };
  }, [rows]);

  if (rows.length < 2) {
    return <div className="empty-state">Not enough match events to draw the probability timeline.</div>;
  }

  const playerA = rows[0]?.player_a || "Player A";
  return (
    <div className="timeline-card">
      <div className="chart-title-row">
        <div>
          <h3>Point Probability Timeline</h3>
          <p>{playerA} point probability, not match-win probability.</p>
        </div>
        <strong>{pct(rows[rows.length - 1]?.point_probability_player_a)}</strong>
      </div>
      <svg className="probability-chart" viewBox={`0 0 ${geometry.width} ${geometry.height}`} role="img" aria-label="Player A point probability timeline">
        <defs>
          <linearGradient id="timelineGradient" x1="0%" x2="100%" y1="0%" y2="0%">
            <stop offset="0%" stopColor="var(--chart-start)" />
            <stop offset="100%" stopColor="var(--chart-end)" />
          </linearGradient>
          <filter id="softGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        {[0, 0.25, 0.5, 0.75, 1].map((tick) => {
          const y = geometry.pad.top + (1 - tick) * geometry.innerH;
          return (
            <g key={tick}>
              <line x1={geometry.pad.left} x2={geometry.pad.left + geometry.innerW} y1={y} y2={y} className={tick === 0.5 ? "midline" : "gridline"} />
              <text x={12} y={y + 4} className="axis-label">{Math.round(tick * 100)}%</text>
            </g>
          );
        })}
        <path d={geometry.path} className="timeline-shadow" />
        <path d={geometry.path} className="timeline-line" filter="url(#softGlow)" />
        {geometry.points.filter((point) => point.event.risk_bucket === "high" || Number(point.event.risk_score || 0) >= 0.7).slice(0, 14).map((point) => (
          <circle key={point.event.event_id} cx={point.x} cy={point.y} r="5" className="risk-marker">
            <title>{`${point.event.risk_bucket} risk, ${pct(point.probability)}`}</title>
          </circle>
        ))}
      </svg>
    </div>
  );
}
