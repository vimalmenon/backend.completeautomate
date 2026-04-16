from fastapi import APIRouter

router = APIRouter()


@router.get("/data", tags=["data"])
def get_data() -> dict[str, str]:
    return {"status": "ok"}
