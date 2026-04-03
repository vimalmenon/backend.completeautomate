import uvicorn
from fastapi import FastAPI

from backend.api.health.health_api import router as health_router
from backend.api.jobs.jobs_api import router as jobs_router

# Keep object name aligned with requested Uvicorn target backend.api.main:main
main = FastAPI(title="CompleteAutomate API")

# Shared API extension for every route.
API_PREFIX = "/api/v1"


# --- Include health router ---
main.include_router(health_router, prefix=API_PREFIX)


# --- Include jobs router ---
main.include_router(jobs_router, prefix=API_PREFIX)


def run_dev() -> None:
    uvicorn.run(
        "backend.api.main:main",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
