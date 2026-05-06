import React from "react";

export default function MiniLineChart({ values = [58, 61, 57, 64, 69, 66, 72], secondary = [42, 48, 46, 51, 56, 53, 59] }) {
  const toPoints = (items) => items.map((value, index) => {
    const x = items.length <= 1 ? 0 : (index / (items.length - 1)) * 300;
    const y = 110 - (Math.max(0, Math.min(100, value)) / 100) * 96;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");
  return (
    <svg viewBox="0 0 300 120" className="mini-line-chart" role="img" aria-label="trend chart">
      {[25, 50, 75].map((tick) => <line key={tick} x1="0" x2="300" y1={116 - tick} y2={116 - tick} />)}
      <polyline points={toPoints(secondary)} className="secondary-line" />
      <polyline points={toPoints(values)} className="primary-line" />
    </svg>
  );
}
