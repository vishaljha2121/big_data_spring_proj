import React, { useMemo, useState } from "react";
import Card from "../components/Card.jsx";
import DataTable from "../components/DataTable.jsx";
import MiniLineChart from "../components/MiniLineChart.jsx";
import { getMatches, getMatchEvents, getSelectedMatch } from "../utils/derivedMetrics.js";
import { compactReplayId, fixed, matchLabel, pct, probability, risk } from "./pageUtils.jsx";

export default function MatchBrowserPage({ data, onSelectMatch, onNavigate }) {
  const matches = getMatches(data);
  const selected = getSelectedMatch(data) || matches[0];
  const [query, setQuery] = useState("");
  const filtered = useMemo(() => matches.filter((match) => matchLabel(match).toLowerCase().includes(query.toLowerCase()) || String(match.synthetic_match_id || "").includes(query)), [matches, query]);
  const rows = filtered.map((match) => ({
    key: match.synthetic_match_id,
    cells: [matchLabel(match), compactReplayId(match.synthetic_match_id), match.event_count || 0, probability(match.avg_point_probability_player_a), risk(Number(match.max_risk_score || 0) >= 0.7 ? "high" : Number(match.max_risk_score || 0) >= 0.4 ? "medium" : "low", match.max_risk_score)],
  }));
  const selectedIndex = filtered.findIndex((match) => match.synthetic_match_id === selected?.synthetic_match_id);
  return (
    <div className="two-column-page">
      <div className="page-stack">
        <Card title="Search and Filters" eyebrow="API-backed match browser">
          <div className="filter-grid">
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search player or Replay ID" />
            <button>Risk bucket ▾</button>
            <button>Replay status ▾</button>
            <button>Local sample</button>
          </div>
          <div className="filter-chips"><span>Real scored sample</span><span>Point probabilities</span><span>No official tournament metadata</span></div>
        </Card>
        <Card title="Match Results">
          <DataTable
            columns={["Players", "Replay ID", "Events", "Avg P(A)", "Max Risk"]}
            rows={rows}
            selectedIndex={selectedIndex}
            onSelect={(index) => onSelectMatch(filtered[index]?.synthetic_match_id)}
          />
        </Card>
      </div>
      <Card title="Selected Match Details">
        <div className="selected-detail">
          <span className="soft-label">Selected match</span>
          <h2>{matchLabel(selected)}</h2>
          {compactReplayId(selected?.synthetic_match_id)}
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
