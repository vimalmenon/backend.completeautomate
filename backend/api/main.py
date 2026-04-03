import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.channel.channel_api import router as channel_router
from backend.api.health.health_api import router as health_router
from backend.api.jobs.jobs_api import router as jobs_router

# Keep object name aligned with requested Uvicorn target backend.api.main:main
main = FastAPI(title="CompleteAutomate API")

# Shared API extension for every route.
API_PREFIX = "/api/v1"

main.add_middleware(
    CORSMiddleware,
    # Browsers send Origin without trailing slash, so keep canonical value.
    allow_origins=["http://localhost:3000", "http://localhost:3000/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Include health router ---
main.include_router(health_router, prefix=API_PREFIX)


# --- Include jobs router ---
main.include_router(jobs_router, prefix=API_PREFIX)


# --- Include channel router ---
main.include_router(channel_router, prefix=API_PREFIX)


def run_dev() -> None:
    uvicorn.run(
        "backend.api.main:main",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
