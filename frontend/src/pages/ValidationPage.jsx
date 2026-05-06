import React from "react";
import Card from "../components/Card.jsx";
import DataTable from "../components/DataTable.jsx";
import { validationItems } from "../utils/derivedMetrics.js";
import { status } from "./pageUtils.jsx";

export default function ValidationPage({ data }) {
  const rows = validationItems(data).map(([name, state, detail]) => ({ cells: [name, status(state), detail] }));
  return (
    <Card title="Validation Center" eyebrow="Final demo evidence">
      <p className="module-note">This page summarizes validation reports produced by repo scripts. It does not invent pass rates.</p>
      <DataTable columns={["Check", "Status", "Evidence"]} rows={rows} />
    </Card>
  );
}
