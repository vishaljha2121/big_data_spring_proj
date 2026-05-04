import React from "react";
import BenchmarkEvidencePanel from "../components/BenchmarkEvidencePanel.jsx";
import HeroHeader from "../components/HeroHeader.jsx";
import KpiStrip from "../components/KpiStrip.jsx";
import Layout from "../components/Layout.jsx";
import MatchAnalyticsPanel from "../components/MatchAnalyticsPanel.jsx";
import MatchesTable from "../components/MatchesTable.jsx";
import ModelArtifactPanel from "../components/ModelArtifactPanel.jsx";
import ModelComparisonPanel from "../components/ModelComparisonPanel.jsx";
import RiskOverviewPanel from "../components/RiskOverviewPanel.jsx";
import ScoredEventsTable from "../components/ScoredEventsTable.jsx";

export default function DashboardPage({ data, theme, onThemeChange, onSelectMatch }) {
  const selectedSurface = data?.matchDetail?.summary?.surface || data?.matchDetail?.surface;
  const surfaceUnavailable = !selectedSurface;
  return (
    <Layout theme={theme}>
      <HeroHeader
        health={data.health}
        ready={data.ready}
        summary={data.summary}
        theme={theme}
        onThemeChange={onThemeChange}
        surfaceUnavailable={surfaceUnavailable}
      />
      <KpiStrip summary={data.summary} benchmarks={data.benchmarks} />
      <div className="insight-grid">
        <MatchAnalyticsPanel matchDetail={data.matchDetail} matchEvents={data.matchEvents} />
        <aside className="insight-rail">
          <RiskOverviewPanel riskSummary={data.riskSummary} riskEvents={data.riskEvents} />
          <ModelComparisonPanel models={data.models} benchmarks={data.benchmarks} />
          <ModelArtifactPanel models={data.models} />
          <BenchmarkEvidencePanel benchmarks={data.benchmarks} />
        </aside>
      </div>
      <section className="data-grid" id="matches">
        <MatchesTable matches={data.matches} selectedMatchId={data.selectedMatchId} onSelectMatch={onSelectMatch} />
        <ScoredEventsTable scoredEvents={data.scoredEvents} />
      </section>
    </Layout>
  );
}
