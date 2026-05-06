import React from "react";
import Sidebar from "./Sidebar.jsx";
import TopHeader from "./TopHeader.jsx";
import FeatureScopeBanner from "./FeatureScopeBanner.jsx";

export default function AppShell({ activePage, onNavigate, apiReady, summary, theme, onThemeChange, children }) {
  return (
    <main className="centre-court-app" data-theme={theme}>
      <Sidebar activePage={activePage} onNavigate={onNavigate} />
      <section className="app-main">
        <TopHeader
          activePage={activePage}
          onNavigate={onNavigate}
          apiReady={apiReady}
          summary={summary}
          theme={theme}
          onThemeChange={onThemeChange}
        />
        <div className="page-wrap">
          <FeatureScopeBanner activePage={activePage} />
          {children}
        </div>
      </section>
    </main>
  );
}
