"""Shared response helpers for API routes."""

from __future__ import annotations

from datetime import datetime, timezone


RISK_DISCLAIMER = (
    "Risk scores are statistical anomaly signals for review only; they are not "
    "proof of misconduct and are not match-fixing detection."
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
