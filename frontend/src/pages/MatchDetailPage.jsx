import React from "react";
import Layout from "../components/Layout.jsx";
import MatchDetail from "../components/MatchDetail.jsx";

export default function MatchDetailPage({ matchDetail, matchEvents }) {
  return (
    <Layout>
      <MatchDetail matchDetail={matchDetail} matchEvents={matchEvents} />
    </Layout>
  );
}
