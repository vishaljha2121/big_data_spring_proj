import React from "react";
import StatusBadge from "../components/StatusBadge.jsx";
import ProbabilityBar from "../components/ProbabilityBar.jsx";
import RiskBadge from "../components/RiskBadge.jsx";
import { compactId, fixed, pct, shortHash } from "../utils/formatting.js";

/**
 * Return true when a player name looks like a real (non-placeholder) name.
 */
export function isRealPlayerName(name) {
  if (!name) return false;
  const lower = name.toLowerCase();
  return lower !== "unknown" && lower !== "player a" && lower !== "player b" && lower !== "unknown player";
}

/**
 * Build a human-readable match title.  Prioritises player names over IDs.
 */
export function displayMatchTitle(matchOrEvent) {
  if (!matchOrEvent) return "No match selected";
  const a = matchOrEvent.player_a || matchOrEvent.primary_match_label;
  const b = matchOrEvent.player_b;
  if (isRealPlayerName(a) && isRealPlayerName(b)) {
    return `${a} vs ${b}`;
  }
  if (matchOrEvent.primary_match_label) return matchOrEvent.primary_match_label;
  return compactId(matchOrEvent.synthetic_match_id);
}

/**
 * Backward-compatible match label.
 */
export function matchLabel(match) {
  return displayMatchTitle(match);
}

/**
 * Render a replay ID as a compact secondary element.
 */
export function displayReplayId(id) {
  if (!id) return "n/a";
  return compactId(id);
}

/**
 * Render a source match ID.
 */
export function displaySourceId(id) {
  if (!id) return null;
  return id;
}

export function status(statusValue) {
  return <StatusBadge status={statusValue}>{statusValue}</StatusBadge>;
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
