import React from "react";
import Card from "../components/Card.jsx";
import ProgressBar from "../components/ProgressBar.jsx";
import DataTable from "../components/DataTable.jsx";
import { getModelMetrics, getScoredEvents, getSelectedMatch } from "../utils/derivedMetrics.js";
import { fixed, matchLabel, pct, probability } from "./pageUtils.jsx";

export default function PredictionCenterPage({ data, onNavigate }) {
  const selected = getSelectedMatch(data);
  const event = getScoredEvents(data)[0] || {};
  const model = getModelMetrics(data);
  const rows = [
    { cells: ["Player A point probability", selected?.player_a || event.player_a || "Player A", probability(event.point_probability_player_a)] },
    { cells: ["Player B point probability", selected?.player_b || event.player_b || "Player B", probability(event.point_probability_player_b)] },
    { cells: ["Model version", model.version, model.modelType] },
    { cells: ["Target", "Player A point winner", "Point-level label"] },
  ];
  return (
    <div className="two-column-page">
      <Card title="Point Scoring Center" eyebrow="No match-winner betting prediction">
        <p className="module-note">This model predicts current point outcome probability. It does not predict official match winners and it is not betting odds.</p>
        <h2>{matchLabel(selected)}</h2>
        <div className="prediction-result">
          <span>Player A point probability</span>
          <strong>{pct(event.point_probability_player_a)}</strong>
          <ProgressBar value={(event.point_probability_player_a || 0) * 100} />
        </div>
      </Card>
      <Card title="Scoring Output" action={<button className="link-action" onClick={() => onNavigate("Model Performance")}>Model details →</button>}>
        <DataTable columns={["Output", "Subject", "Value"]} rows={rows} />
        <p className="muted-copy">Feature count: {model.featureCount}; test AUC {fixed(model.testAuc, 3)}; test Brier {fixed(model.testBrier, 3)}.</p>
      </Card>
    </div>
  );
}
