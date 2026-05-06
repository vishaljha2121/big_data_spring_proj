import React, { useEffect, useMemo, useState } from "react";
import { loadDashboardData } from "./api/client.js";
import AppShell from "./shell/AppShell.jsx";
import LoadingState from "./components/LoadingState.jsx";
import ErrorState from "./components/ErrorState.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import MatchBrowserPage from "./pages/MatchBrowserPage.jsx";
import ReplayCenterPage from "./pages/ReplayCenterPage.jsx";
import PointTimelinePage from "./pages/PointTimelinePage.jsx";
import ReplayManifestPage from "./pages/ReplayManifestPage.jsx";
import PredictionCenterPage from "./pages/PredictionCenterPage.jsx";
import ModelPerformancePage from "./pages/ModelPerformancePage.jsx";
import DataExplorerPage from "./pages/DataExplorerPage.jsx";
import ValidationPage from "./pages/ValidationPage.jsx";
import PipelineMonitorPage from "./pages/PipelineMonitorPage.jsx";
import ReportsPage from "./pages/ReportsPage.jsx";
import PlayersPage from "./pages/PlayersPage.jsx";
import PlayerComparisonPage from "./pages/PlayerComparisonPage.jsx";
import TournamentsPage from "./pages/TournamentsPage.jsx";
import SurfaceAnalyticsPage from "./pages/SurfaceAnalyticsPage.jsx";
import RankingsPage from "./pages/RankingsPage.jsx";
import { normalizeSurfaceTheme } from "./theme/surfaceThemes.js";

export default function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [selectedMatchId, setSelectedMatchId] = useState(null);
  const [activePage, setActivePage] = useState("Dashboard");
  const [theme, setTheme] = useState("clay");

  useEffect(() => {
    let alive = true;
    setError(null);
    loadDashboardData(selectedMatchId)
      .then((payload) => {
        if (!alive) return;
        setData(payload);
        setSelectedMatchId(payload.selectedMatchId);
      })
      .catch((err) => {
        if (!alive) return;
        setError(err);
      });
    return () => {
      alive = false;
    };
  }, [selectedMatchId]);

  const page = useMemo(() => {
    if (!data) return null;
    const common = {
      data,
      onNavigate: setActivePage,
      onSelectMatch: setSelectedMatchId,
    };
    switch (activePage) {
      case "Dashboard":
        return <DashboardPage {...common} />;
      case "Match Browser":
        return <MatchBrowserPage {...common} />;
      case "Players":
        return <PlayersPage {...common} />;
      case "Player Comparison":
        return <PlayerComparisonPage {...common} />;
      case "Tournaments":
        return <TournamentsPage {...common} />;
      case "Surface Analytics":
        return <SurfaceAnalyticsPage {...common} />;
      case "Rankings":
        return <RankingsPage {...common} />;
      case "Replay Center":
        return <ReplayCenterPage {...common} />;
      case "Point Timeline":
        return <PointTimelinePage {...common} />;
      case "Replay Manifest":
        return <ReplayManifestPage {...common} />;
      case "Prediction Center":
        return <PredictionCenterPage {...common} />;
      case "Model Performance":
        return <ModelPerformancePage {...common} />;
      case "Data Explorer":
        return <DataExplorerPage {...common} />;
      case "Validation":
        return <ValidationPage {...common} />;
      case "Pipeline Monitor":
        return <PipelineMonitorPage {...common} />;
      case "Reports":
        return <ReportsPage {...common} />;
      default:
        return <DashboardPage {...common} />;
    }
  }, [activePage, data]);

  if (error) return <ErrorState error={error} />;
  if (!data) return <LoadingState />;

  const apiReady = data.health?.status === "ok" && data.ready?.status === "ready";
  const selectedSurface = data.matchDetail?.surface || data.matchDetail?.item?.surface;
  const effectiveTheme = theme || normalizeSurfaceTheme(selectedSurface);
  return (
    <AppShell
      activePage={activePage}
      onNavigate={setActivePage}
      apiReady={apiReady}
      summary={data.summary}
      theme={effectiveTheme}
      onThemeChange={setTheme}
    >
      {page}
    </AppShell>
  );
}
