import React from "react";
import { FEATURE_SCOPE } from "./navigation.js";

export default function FeatureScopeBanner({ activePage }) {
  return (
    <div className="feature-scope">
      <strong>Feature scope:</strong>
      <span>{FEATURE_SCOPE[activePage] || FEATURE_SCOPE.Dashboard}</span>
    </div>
  );
}
