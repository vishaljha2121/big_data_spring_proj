import React from "react";
import { surfaceThemes } from "../theme/surfaceThemes.js";

export default function ThemeSwitcher({ theme, onThemeChange }) {
  return (
    <div className="theme-switcher" aria-label="Court surface theme">
      {Object.values(surfaceThemes).map((item) => (
        <button
          type="button"
          key={item.key}
          className={theme === item.key ? "active" : ""}
          onClick={() => onThemeChange(item.key)}
          title={item.note}
        >
          {item.label}
        </button>
      ))}
    </div>
  );
}
