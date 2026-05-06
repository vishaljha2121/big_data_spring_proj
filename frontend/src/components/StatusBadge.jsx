import React from "react";

export default function StatusBadge({ status = "planned", children }) {
  const normalized = String(status || "planned").toLowerCase();
  return <span className={`status-badge ${normalized}`}>{children || status}</span>;
}
