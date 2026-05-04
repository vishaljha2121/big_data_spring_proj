export function number(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "n/a";
  return Number(value).toLocaleString(undefined, { maximumFractionDigits: digits });
}

export function percent(value, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "n/a";
  return `${(Number(value) * 100).toFixed(digits)}%`;
}

export function shortHash(value) {
  if (!value) return "n/a";
  return `${value.slice(0, 10)}...`;
}

export function compactId(value) {
  if (!value) return "n/a";
  return value.length > 24 ? `${value.slice(0, 12)}...${value.slice(-6)}` : value;
}

export function fixed(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "n/a";
  return Number(value).toFixed(digits);
}

export function pct(value, digits = 1) {
  return percent(value, digits);
}

export function bucketClass(bucket) {
  return `risk-${String(bucket || "unknown").toLowerCase()}`;
}
