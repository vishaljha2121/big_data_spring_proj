import React from "react";

export default function Layout({ children, theme = "clay" }) {
  return (
    <main className="app-root" data-theme={theme}>
      <div className="court-lines" aria-hidden="true" />
      <div className="shell">{children}</div>
    </main>
  );
}
