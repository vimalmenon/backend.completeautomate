from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.auth.auth_api import router as auth_router
from backend.api.auth.dependencies import get_current_user
from backend.api.auth.openapi import (
    get_swagger_ui_init_oauth,
    inject_security_scheme,
)
from backend.api.channel.channel_api import router as channel_router
from backend.api.data.data_api import router as data_router
from backend.api.health.health_api import router as health_router
from backend.api.jobs.jobs_api import router as jobs_router
from backend.api.prompts.prompts_api import router as prompts_router
from backend.api.prompts.prompts_dashboard import router as prompts_dashboard_router
from backend.config.env import env
from backend.manager import DataManager


def initialize_api_data() -> None:
    if env.OFFLINE:
        DataManager().upload()


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_api_data()
    yield


# Keep object name aligned with requested Uvicorn target backend.api.main:main
swagger_oauth = get_swagger_ui_init_oauth()
main = FastAPI(
    title="CompleteAutomate API",
    lifespan=lifespan,
    swagger_ui_init_oauth=swagger_oauth,
)


# Custom OpenAPI schema to inject Cognito OAuth2 security scheme
def custom_openapi() -> dict:
    if main.openapi_schema is not None:
        return main.openapi_schema
    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title="CompleteAutomate API",
        version="0.0.1",
        description="",
        routes=main.routes,
    )
    openapi_schema = inject_security_scheme(openapi_schema)
    main.openapi_schema = openapi_schema
    return main.openapi_schema


main.openapi = custom_openapi  # type: ignore[assignment]

# Shared API extension for every route.
API_PREFIX = "/api/v1"

main.add_middleware(
    CORSMiddleware,
    # Browsers send Origin without trailing slash, so keep canonical value.
    allow_origins=env.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Include auth router (public) ---
main.include_router(auth_router, prefix=API_PREFIX)


# --- Include health router ---
main.include_router(health_router, prefix=API_PREFIX)


# --- Include jobs router (protected) ---
main.include_router(
    jobs_router,
    prefix=API_PREFIX,
    dependencies=[Depends(get_current_user)],
)


# --- Include channel router (protected) ---
main.include_router(
    channel_router,
    prefix=API_PREFIX,
    dependencies=[Depends(get_current_user)],
)


# --- Include prompts router (protected) ---
main.include_router(
    prompts_router,
    prefix=API_PREFIX,
    dependencies=[Depends(get_current_user)],
)


# --- Include prompts dashboard router (protected) ---
main.include_router(
    prompts_dashboard_router,
    prefix=API_PREFIX,
    dependencies=[Depends(get_current_user)],
)


# --- Include data router (protected) ---
main.include_router(
    data_router,
    prefix=API_PREFIX,
    dependencies=[Depends(get_current_user)],
)


def run_dev() -> None:
    uvicorn.run(
        "backend.api.main:main",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
