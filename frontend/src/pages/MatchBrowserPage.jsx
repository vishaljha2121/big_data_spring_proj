import React, { useEffect, useMemo, useState } from "react";
import Card from "../components/Card.jsx";
import DataTable from "../components/DataTable.jsx";
import MiniLineChart from "../components/MiniLineChart.jsx";
import { getMatches, getMatchEvents, getSelectedMatch } from "../utils/derivedMetrics.js";
import { getReplayMatches } from "../api/client.js";
import { compactReplayId, displayMatchTitle, fixed, pct, probability, risk } from "./pageUtils.jsx";

export default function MatchBrowserPage({ data, onSelectMatch, onNavigate }) {
  const matches = getMatches(data);
  const selected = getSelectedMatch(data) || matches[0];
  const [query, setQuery] = useState("");
  const [activeTab, setActiveTab] = useState("scored");
  const [replayCatalog, setReplayCatalog] = useState(data?.replayMatches?.items || []);
  const [replayLoading, setReplayLoading] = useState(false);

  // Load replay catalog when tab changes
  useEffect(() => {
    if (activeTab === "catalog" && replayCatalog.length === 0) {
      setReplayLoading(true);
      getReplayMatches({ limit: 200, search: query || undefined })
        .then((res) => setReplayCatalog(res.items || []))
        .catch(() => {})
        .finally(() => setReplayLoading(false));
    }
  }, [activeTab]);

  // Search within replay catalog
  useEffect(() => {
    if (activeTab === "catalog" && query) {
      setReplayLoading(true);
      getReplayMatches({ limit: 200, search: query })
        .then((res) => setReplayCatalog(res.items || []))
        .catch(() => {})
        .finally(() => setReplayLoading(false));
    }
  }, [query, activeTab]);

  const filtered = useMemo(() =>
    matches.filter((match) =>
      displayMatchTitle(match).toLowerCase().includes(query.toLowerCase()) ||
      String(match.synthetic_match_id || "").includes(query)
    ),
    [matches, query]
  );

  const scoredRows = filtered.map((match) => ({
    key: match.synthetic_match_id,
    cells: [
      displayMatchTitle(match),
      match.event_count || 0,
      probability(match.avg_point_probability_player_a),
      risk(
        Number(match.max_risk_score || 0) >= 0.7 ? "high" : Number(match.max_risk_score || 0) >= 0.4 ? "medium" : "low",
        match.max_risk_score
      ),
    ],
  }));

  const catalogRows = replayCatalog.map((match) => ({
    key: match.synthetic_match_id,
    cells: [
      match.primary_match_label || displayMatchTitle(match),
      match.replay_event_count || 0,
      match.scored_available ? "✓ Scored" : "Raw only",
      compactReplayId(match.synthetic_match_id),
    ],
  }));

  const selectedIndex = filtered.findIndex((match) => match.synthetic_match_id === selected?.synthetic_match_id);
  return (
    <div className="two-column-page">
      <div className="page-stack">
        <Card title="Search and Filters" eyebrow="API-backed match browser">
          <div className="filter-grid">
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search player name or match ID" />
            <button className={activeTab === "scored" ? "primary-action" : ""} onClick={() => setActiveTab("scored")}>Scored Matches</button>
            <button className={activeTab === "catalog" ? "primary-action" : ""} onClick={() => setActiveTab("catalog")}>Full Replay Catalog</button>
          </div>
          <div className="filter-chips">
            {activeTab === "scored"
              ? <><span>Real scored sample</span><span>Point probabilities</span><span>No official tournament metadata</span></>
              : <><span>Full replay manifest</span><span>{replayCatalog.length} matches loaded</span><span>Raw events + scored where available</span></>
            }
          </div>
        </Card>
        <Card title={activeTab === "scored" ? "Scored Match Results" : "Replay Catalog"}>
          {activeTab === "scored" ? (
            <DataTable
              columns={["Players", "Events", "Avg P(A)", "Max Risk"]}
              rows={scoredRows}
              selectedIndex={selectedIndex}
              onSelect={(index) => onSelectMatch(filtered[index]?.synthetic_match_id)}
            />
          ) : replayLoading ? (
            <p className="muted-copy">Loading replay catalog…</p>
          ) : (
            <DataTable
              columns={["Players", "Events", "Scored?", "Replay ID"]}
              rows={catalogRows}
              onSelect={(index) => {
                const m = replayCatalog[index];
                if (m?.scored_available) {
                  onSelectMatch(m.synthetic_match_id);
                  setActiveTab("scored");
                }
              }}
            />
          )}
        </Card>
      </div>
      <Card title="Selected Match Details">
        <div className="selected-detail">
          <h2>{displayMatchTitle(selected)}</h2>
          <span className="soft-label">Replay ID</span>
          {compactReplayId(selected?.synthetic_match_id)}
          {selected?.source_match_id && (
            <><span className="soft-label" style={{ marginTop: "0.25rem" }}>Source ID</span><code className="replay-id">{selected.source_match_id}</code></>
          )}
          <div className="detail-metrics">
            <p><span>Events</span><strong>{selected?.event_count || getMatchEvents(data).length || 0}</strong></p>
            <p><span>Avg P(A)</span><strong>{pct(selected?.avg_point_probability_player_a)}</strong></p>
            <p><span>Max risk</span><strong>{fixed(selected?.max_risk_score, 3)}</strong></p>
          </div>
          <MiniLineChart values={getMatchEvents(data).slice(0, 8).map((event) => Number(event.point_probability_player_a || 0) * 100)} />
          <button className="primary-action full" onClick={() => onNavigate("Replay Center")}>View Replay</button>
          <button className="secondary-action full" onClick={() => onNavigate("Point Timeline")}>Open Point Timeline</button>
          <button className="secondary-action full" onClick={() => onNavigate("Player Comparison")}>Compare Players</button>
        </div>
      </Card>
    </div>
  );
}
