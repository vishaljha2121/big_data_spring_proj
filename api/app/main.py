"""FastAPI entrypoint for the local file-backed tennis scoring API."""

from fastapi import FastAPI

from api.app.config import settings
from api.app.routes import benchmarks, health, matches, models, risk, scored_events


app = FastAPI(
    title="Tennis Scoring API",
    version=settings.version,
    description=(
        "File-backed API over validated scored tennis point events. Point probabilities "
        "are point-level model outputs, not betting odds or match-win probabilities."
    ),
)

app.include_router(health.router)
app.include_router(benchmarks.router)
app.include_router(scored_events.router)
app.include_router(matches.router)
app.include_router(risk.router)
app.include_router(models.router)
