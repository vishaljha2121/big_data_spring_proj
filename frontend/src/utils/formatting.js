// ──────────────────────────────────────────────────────────────
// Formatting utilities for the CourtIQ dashboard
// ──────────────────────────────────────────────────────────────

// ── Numeric formatting ──────────────────────────────────────

export function number(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "n/a";
  return Number(value).toLocaleString(undefined, { maximumFractionDigits: digits });
}

export function percent(value, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "n/a";
  return `${(Number(value) * 100).toFixed(digits)}%`;
}

export function fixed(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "n/a";
  return Number(value).toFixed(digits);
}

export function pct(value, digits = 1) {
  return percent(value, digits);
}

// ── ID / hash display ───────────────────────────────────────

export function shortHash(value) {
  if (!value) return "n/a";
  return `${value.slice(0, 10)}…`;
}

export function compactId(value) {
  if (!value) return "n/a";
  return value.length > 24 ? `${value.slice(0, 12)}…${value.slice(-6)}` : value;
}

export function bucketClass(bucket) {
  return `risk-${String(bucket || "unknown").toLowerCase()}`;
}

// ── Match display helpers ───────────────────────────────────

/**
 * Returns true when a player name looks like a real (non-placeholder) name.
 */
export function isRealPlayerName(name) {
  if (!name) return false;
  const lower = name.toLowerCase();
  return lower !== "unknown" && lower !== "player a" && lower !== "player b" && lower !== "unknown player";
}

/**
 * Returns true when both player names exist and are not just
 * generic fallback values.
 */
export function hasRealPlayers(matchOrEvent) {
  if (!matchOrEvent) return false;
  return isRealPlayerName(matchOrEvent.player_a) && isRealPlayerName(matchOrEvent.player_b);
}

/**
 * Build a human-readable match title.
 * Prioritises player names; falls back to a compact replay ID.
 */
export function displayMatchTitle(match) {
  if (!match) return "No match selected";
  if (hasRealPlayers(match)) {
    return `${match.player_a} vs ${match.player_b}`;
  }
  if (match.primary_match_label) return match.primary_match_label;
  return compactId(match?.synthetic_match_id);
}

/**
 * Render a replay ID in a short, secondary style.
 * e.g. "synthetic_ma…692463"
 */
export function displayReplayId(id) {
  if (!id) return "n/a";
  return compactId(id);
}

/**
 * Display a source match ID.
 */
export function displaySourceId(id) {
  if (!id) return null;
  return id;
}

// ── Label humanization ──────────────────────────────────────

const KNOWN_KEY_MAP = {
  return_point_win_pct: "Return point win %",
  serve_point_win_pct: "Serve point win %",
  ace_rate: "Ace rate",
  double_fault_rate: "Double fault rate",
  label_point_winner_is_player_a: "Player A point winner label",
  label_server_won_point: "Server won point label",
  baseline_deviation_score_v1: "Baseline deviation score",
  schema_version: "Schema version",
  feature_schema_hash: "Feature schema hash",
  fake_labels_used: "Fake labels used",
  risk_method: "Risk method",
  model_type: "Model type",
  target_column: "Target column",
  feature_count: "Feature count",
  points_played_before: "Points played",
  player_a_points_won_before: "Player A points won",
  player_b_points_won_before: "Player B points won",
  player_a_point_win_pct_before: "Player A point win %",
  player_b_point_win_pct_before: "Player B point win %",
  server_points_played_before: "Server points played",
  server_points_won_before: "Server points won",
  server_point_win_pct_before: "Server point win %",
  receiver_points_played_before: "Receiver points played",
  receiver_points_won_before: "Receiver points won",
  receiver_point_win_pct_before: "Receiver point win %",
  player_a_recent_5_win_pct_before: "Player A recent‑5 win %",
  player_b_recent_5_win_pct_before: "Player B recent‑5 win %",
  player_a_recent_10_win_pct_before: "Player A recent‑10 win %",
  player_b_recent_10_win_pct_before: "Player B recent‑10 win %",
  player_a_aces_before: "Player A aces",
  player_b_aces_before: "Player B aces",
  player_a_double_faults_before: "Player A double faults",
  player_b_double_faults_before: "Player B double faults",
  elapsed_seconds_before: "Elapsed seconds",
  elapsed_seconds_delta_from_prev: "Seconds since prev point",
  is_server_player_a: "Server is Player A",
  is_receiver_player_a: "Receiver is Player A",
  has_valid_point_winner: "Valid point winner flag",
  has_valid_server: "Valid server flag",
  has_elapsed_seconds: "Has elapsed seconds",
  primary_risk_signal: "Primary signal",
  risk_score: "Risk score",
  risk_bucket: "Risk bucket",
  point_probability_player_a: "Player A point %",
  point_probability_player_b: "Player B point %",
  avg_point_probability_player_a: "Avg Player A point %",
  max_risk_score: "Max risk score",
  high_risk_event_count: "High‑risk events",
  event_count: "Events",
};

const KNOWN_MODEL_MAP = {
  HistGradientBoostingClassifier: "HistGradientBoosting classifier",
  hist_gradient_boosting: "HistGradientBoosting classifier",
  LogisticRegression: "Logistic regression",
  logistic_regression: "Logistic regression",
};

const PRESERVE_ACRONYMS = ["AUC", "API", "JSONL", "p95", "p50", "p99", "ID", "ATP", "ROI", "CLV", "ELO", "MVP", "JSON"];

function titleCasePreserving(text) {
  return text
    .split(/\s+/)
    .map((word) => {
      const upper = word.toUpperCase();
      if (PRESERVE_ACRONYMS.includes(upper)) return upper;
      if (PRESERVE_ACRONYMS.includes(word)) return word;
      return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    })
    .join(" ");
}

/**
 * Convert a raw snake_case / technical key into a human-readable label.
 */
export function humanizeKey(value) {
  if (value === null || value === undefined) return "n/a";
  const s = String(value);
  if (KNOWN_KEY_MAP[s]) return KNOWN_KEY_MAP[s];
  return titleCasePreserving(s.replace(/_/g, " "));
}

/**
 * Humanize a risk/anomaly signal name.
 */
export function humanizeSignal(value) {
  if (!value || value === "none") return "No signal";
  return humanizeKey(value);
}

/**
 * Humanize a target column name.
 */
export function humanizeTarget(value) {
  if (!value) return "n/a";
  return KNOWN_KEY_MAP[value] || humanizeKey(value);
}

/**
 * Humanize a boolean configuration label like "fake_labels_used=false".
 */
export function humanizeBooleanLabel(key, value) {
  if (key === "fake_labels_used") {
    return value === false || value === "false" ? "No fake labels used" : "Fake labels used";
  }
  const label = humanizeKey(key);
  return `${label}: ${value}`;
}

/**
 * Humanize a metric name (used in benchmark / eval displays).
 */
export function humanizeMetricName(value) {
  if (!value) return "n/a";
  const s = String(value);
  if (KNOWN_KEY_MAP[s]) return KNOWN_KEY_MAP[s];
  // Handle metric patterns like test_auc, validation_brier_score
  return titleCasePreserving(s.replace(/_/g, " "));
}

/**
 * Humanize a model type string.
 */
export function humanizeModelType(value) {
  if (!value) return "n/a";
  return KNOWN_MODEL_MAP[value] || value;
}
