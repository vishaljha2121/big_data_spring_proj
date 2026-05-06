import React from "react";
import StatusBadge from "../components/StatusBadge.jsx";
import ProbabilityBar from "../components/ProbabilityBar.jsx";
import RiskBadge from "../components/RiskBadge.jsx";
import { compactId, fixed, pct, shortHash } from "../utils/formatting.js";

export function matchLabel(match) {
  if (!match) return "No match selected";
  return `${match.player_a || "Player A"} vs ${match.player_b || "Player B"}`;
}

export function status(status) {
  return <StatusBadge status={status}>{status}</StatusBadge>;
}

export function probability(value) {
  return <ProbabilityBar value={value} />;
}

export function risk(bucket, score) {
  return <RiskBadge bucket={bucket} score={score} />;
}

export function compactReplayId(value) {
  return <code className="replay-id" title={value}>{compactId(value)}</code>;
}

export { fixed, pct, shortHash };
