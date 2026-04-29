from typing import Any

from fastapi import APIRouter

from backend.manager import DataManager, FileSync

router = APIRouter()


@router.get("/data", tags=["data"])
async def get_data() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/data/download_to_local", tags=["data"])
async def download_to_local() -> dict[str, str]:
    DataManager().download_to_local()
    return {"status": "ok"}


@router.post("/data/upload_to_s3", tags=["data"])
async def upload_to_s3() -> None:
    # TODO Need to implement this
    pass


@router.get("/data/file_synced", tags=["data"])
async def file_synced() -> dict[str, Any]:
    is_synced = FileSync().check()
    return {"synced": is_synced}
