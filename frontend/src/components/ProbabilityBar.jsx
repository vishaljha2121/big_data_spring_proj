import React from "react";
import { pct } from "../utils/formatting.js";

export default function ProbabilityBar({ value, label }) {
  const numeric = Math.max(0, Math.min(1, Number(value || 0)));
  return (
    <div className="probability-cell" aria-label={`${label || "probability"} ${pct(numeric)}`}>
      <div className="probability-track">
        <span style={{ width: `${numeric * 100}%` }} />
      </div>
      <strong>{pct(numeric)}</strong>
    </div>
  );
}
