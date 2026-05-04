import React from "react";
import BenchmarkPanel from "../components/BenchmarkPanel.jsx";
import Layout from "../components/Layout.jsx";
import MatchDetail from "../components/MatchDetail.jsx";
import MatchesTable from "../components/MatchesTable.jsx";
import ModelInfo from "../components/ModelInfo.jsx";
import RiskSummary from "../components/RiskSummary.jsx";
import ScoredEventsTable from "../components/ScoredEventsTable.jsx";
import StatusBanner from "../components/StatusBanner.jsx";
import SummaryCards from "../components/SummaryCards.jsx";

export default function DashboardPage({ data, onSelectMatch }) {
  return (
    <Layout>
      <StatusBanner health={data.health} ready={data.ready} summary={data.summary} />
      <SummaryCards summary={data.summary} benchmarks={data.benchmarks} />
      <div className="grid-two">
        <RiskSummary riskSummary={data.riskSummary} riskEvents={data.riskEvents} />
        <ModelInfo models={data.models} />
      </div>
      <BenchmarkPanel benchmarks={data.benchmarks} />
      <MatchesTable matches={data.matches} selectedMatchId={data.selectedMatchId} onSelectMatch={onSelectMatch} />
      <MatchDetail matchDetail={data.matchDetail} matchEvents={data.matchEvents} />
      <ScoredEventsTable scoredEvents={data.scoredEvents} />
    </Layout>
  );
}
