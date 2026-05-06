import React from "react";
import Card from "../components/Card.jsx";
import DataTable from "../components/DataTable.jsx";
import StatusBadge from "../components/StatusBadge.jsx";

export default function TournamentsPage() {
  const rows = [
    { cells: ["Tournament metadata", "Not exposed by API", "Planned", <StatusBadge status="planned">Planned</StatusBadge>] },
    { cells: ["Round filters", "Requires richer match metadata", "Planned", <StatusBadge status="planned">Planned</StatusBadge>] },
    { cells: ["Official event calendar", "Outside validated source data", "Reference only", <StatusBadge status="planned">Planned</StatusBadge>] },
  ];
  return (
    <Card title="Tournament Explorer" eyebrow="Planned module">
      <p className="module-note">The final API exposes scored replay matches, not official tournament metadata. This page keeps the product shell without inventing tournament facts.</p>
      <DataTable columns={["Capability", "Current Data Source", "Decision", "Status"]} rows={rows} />
    </Card>
  );
}
