"""FastAPI entrypoint for the local file-backed tennis scoring API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.app.config import settings
from api.app.routes import benchmarks, health, matches, models, replay, risk, scored_events


app = FastAPI(
    title="Tennis Scoring API",
    version=settings.version,
    description=(
        "File-backed API over validated scored tennis point events. Point probabilities "
        "are point-level model outputs, not betting odds or match-win probabilities."
    ),
)

# Local demo dashboard runs from Vite on 127.0.0.1:5173. CORS is intentionally
# narrow and limited to browser demo origins rather than opening a production
# policy.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_origin_regex=r"http://(127\.0\.0\.1|localhost):\d+",
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(benchmarks.router)
app.include_router(scored_events.router)
app.include_router(matches.router)
app.include_router(replay.router)
app.include_router(risk.router)
app.include_router(models.router)
