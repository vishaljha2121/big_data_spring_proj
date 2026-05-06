import React from "react";
import Card from "../components/Card.jsx";
import { reportItems } from "../utils/derivedMetrics.js";

export default function ReportsPage() {
  return (
    <Card title="Reports and Audit Documents" eyebrow="Local repo documentation">
      <div className="report-grid">
        {reportItems().map(([name, path, description]) => (
          <article key={path} className="report-card">
            <strong>{name}</strong>
            <span>{path}</span>
            <p>{description}</p>
          </article>
        ))}
      </div>
    </Card>
  );
}
