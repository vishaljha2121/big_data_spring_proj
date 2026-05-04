export const surfaceThemes = {
  clay: {
    key: "clay",
    label: "Clay",
    note: "Roland Garros-inspired clay court demo theme",
  },
  hard: {
    key: "hard",
    label: "Hard",
    note: "Blue hard-court analytics theme",
  },
  grass: {
    key: "grass",
    label: "Grass",
    note: "Grass-court analytics theme",
  },
  neutral: {
    key: "neutral",
    label: "Neutral",
    note: "Neutral presentation theme",
  },
};

export function normalizeSurfaceTheme(surface) {
  const value = String(surface || "").toLowerCase();
  if (value.includes("clay")) return "clay";
  if (value.includes("hard")) return "hard";
  if (value.includes("grass")) return "grass";
  return "clay";
}
