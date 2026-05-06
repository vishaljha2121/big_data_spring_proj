import React from "react";
import Card from "../components/Card.jsx";
import DataTable from "../components/DataTable.jsx";
import StatusBadge from "../components/StatusBadge.jsx";

export default function DataExplorerPage() {
  const rows = [
    { cells: ["Curated singles points", "Parquet", "1,922,136", <StatusBadge status="PASSED">PASSED</StatusBadge>] },
    { cells: ["Match features", "Parquet", "10,508", <StatusBadge status="PASSED">PASSED</StatusBadge>] },
    { cells: ["Player baselines", "Parquet", "1,891", <StatusBadge status="PASSED">PASSED</StatusBadge>] },
    { cells: ["Replay manifest", "Parquet", "1,917,672 events", <StatusBadge status="PASSED">PASSED</StatusBadge>] },
    { cells: ["Scored events sample", "JSONL/Parquet", "1,000", <StatusBadge status="PASSED">PASSED</StatusBadge>] },
    { cells: ["API sample responses", "JSON", "documented", <StatusBadge status="PASSED">PASSED</StatusBadge>] },
  ];
  return (
    <Card title="Data Explorer" eyebrow="Validated project artifacts">
      <p className="module-note">Counts are project summary values from validated local artifacts, not live database queries.</p>
      <DataTable columns={["Dataset", "Type", "Rows", "Status"]} rows={rows} />
    </Card>
  );
}
