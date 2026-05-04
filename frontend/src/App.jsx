import React, { useEffect, useState } from "react";
import DashboardPage from "./pages/DashboardPage.jsx";
import { loadDashboardData } from "./api/client.js";
import LoadingState from "./components/LoadingState.jsx";
import ErrorState from "./components/ErrorState.jsx";
import { normalizeSurfaceTheme } from "./theme/surfaceThemes.js";

export default function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [selectedMatchId, setSelectedMatchId] = useState(null);
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

  const selectedSurface = data?.matchDetail?.summary?.surface || data?.matchDetail?.surface;
  const activeTheme = theme || normalizeSurfaceTheme(selectedSurface);

  if (error) return <ErrorState error={error} />;
  if (!data) return <LoadingState />;
  return (
    <DashboardPage
      data={data}
      theme={activeTheme}
      onThemeChange={setTheme}
      onSelectMatch={setSelectedMatchId}
    />
  );
}
