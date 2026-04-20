from fastapi import APIRouter

from backend.manager import HealthManager

router = APIRouter()


@router.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return HealthManager().check()
