const API_BASE_URL = (window.__API_BASE_URL__ || import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");

async function request(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`${path} returned ${response.status}`);
  }
  return response.json();
}

export function getHealth() {
  return request("/health");
}

export function getReady() {
  return request("/ready");
}

export function getSummary() {
  return request("/api/summary");
}

export function getScoredEvents(params = {}) {
  const query = new URLSearchParams({ limit: params.limit || 100, offset: params.offset || 0 });
  if (params.riskBucket) query.set("risk_bucket", params.riskBucket);
  if (params.matchId) query.set("match_id", params.matchId);
  return request(`/api/scored-events?${query.toString()}`);
}

export function getMatches(params = {}) {
  const query = new URLSearchParams({ limit: params.limit || 100, offset: params.offset || 0 });
  return request(`/api/matches?${query.toString()}`);
}

export function getMatchDetail(matchId) {
  return request(`/api/matches/${encodeURIComponent(matchId)}`);
}

export function getMatchEvents(matchId, params = {}) {
  const query = new URLSearchParams({ limit: params.limit || 2000, offset: params.offset || 0 });
  return request(`/api/matches/${encodeURIComponent(matchId)}/events?${query.toString()}`);
}

export function getRiskSummary() {
  return request("/api/risk/summary");
}

export function getRiskEvents(params = {}) {
  const query = new URLSearchParams({ limit: params.limit || 100, offset: params.offset || 0 });
  if (params.bucket) query.set("bucket", params.bucket);
  return request(`/api/risk/events?${query.toString()}`);
}

export function getModelInfo() {
  return request("/api/models/current");
}

export function getBenchmarkInfo() {
  return request("/api/benchmarks/latest");
}

// ── New Milestone 5B endpoints ───────────────────────────────

export function getDataCoverage() {
  return request("/api/data/coverage");
}

export function getObservabilitySummary() {
  return request("/api/observability/summary");
}

export function getObservabilityAlerts() {
  return request("/api/observability/alerts");
}

export function getObservabilityMetrics() {
  return request("/api/observability/metrics");
}

export function getOutcomeModels() {
  return request("/api/models/outcomes");
}

export function getReplayMatches(params = {}) {
  const query = new URLSearchParams({ limit: params.limit || 100, offset: params.offset || 0 });
  if (params.search) query.set("search", params.search);
  return request(`/api/replay/matches?${query.toString()}`);
}

export function getReplayMatchEvents(matchId, params = {}) {
  const query = new URLSearchParams({ limit: params.limit || 1000, offset: params.offset || 0 });
  return request(`/api/replay/matches/${encodeURIComponent(matchId)}/events?${query.toString()}`);
}

export async function loadDashboardData(selectedMatchId = null) {
  const [
    health,
    ready,
    summary,
    scoredEvents,
    matches,
    riskSummary,
    riskEvents,
    models,
    benchmarks,
    dataCoverage,
    replayMatches,
    observability,
    outcomes
  ] = await Promise.all([
    getHealth(),
    getReady(),
    getSummary(),
    getScoredEvents({ limit: 100 }),
    getMatches({ limit: 100 }),
    getRiskSummary(),
    getRiskEvents({ limit: 100 }),
    getModelInfo(),
    getBenchmarkInfo(),
    getDataCoverage().catch(() => null),
    getReplayMatches({ limit: 100 }).catch(() => null),
    getObservabilitySummary().catch(() => null),
    getOutcomeModels().catch(() => null)
  ]);
  const matchId = selectedMatchId || (matches.items && matches.items[0] && matches.items[0].synthetic_match_id) || null;
  const matchDetail = matchId ? await getMatchDetail(matchId) : null;
  const matchEvents = matchId ? await getMatchEvents(matchId, { limit: 2000 }) : null;
  return {
    health,
    ready,
    summary,
    scoredEvents,
    matches,
    riskSummary,
    riskEvents,
    models,
    benchmarks,
    matchDetail,
    matchEvents,
    dataCoverage,
    replayMatches,
    observability,
    outcomes,
    selectedMatchId: matchId
  };
}
