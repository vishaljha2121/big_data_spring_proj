import React from "react";
import { bucketClass, fixed } from "../utils/formatting.js";

export default function RiskBadge({ bucket, score, compact = false }) {
  const label = bucket || "unknown";
  return (
    <span className={`risk-badge ${bucketClass(label)}`}>
      <span>{label}</span>
      {!compact && score !== undefined && score !== null ? <strong>{fixed(score, 3)}</strong> : null}
    </span>
  );
}
