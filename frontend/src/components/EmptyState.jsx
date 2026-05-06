import React from "react";

export default function EmptyState({ title = "Module planned", children }) {
  return (
    <div className="empty-module">
      <strong>{title}</strong>
      <p>{children}</p>
    </div>
  );
}
