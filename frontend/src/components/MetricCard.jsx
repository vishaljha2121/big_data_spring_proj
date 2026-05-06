import React from "react";

export default function MetricCard({ label, value, sub, accent = "purple" }) {
  return (
    <article className={`metric-tile accent-${accent}`}>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        <small>{sub}</small>
      </div>
      <i aria-hidden="true">●</i>
    </article>
  );
}
