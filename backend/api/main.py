import uvicorn
from fastapi import FastAPI

# Keep object name aligned with requested Uvicorn target backend.api.main:main
main = FastAPI(title="CompleteAutomate API")


@main.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@main.get("/test", tags=["test"])
def test_route() -> dict[str, str]:
    return {"message": "test route working"}


def run_dev() -> None:
    uvicorn.run(
        "backend.api.main:main",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
