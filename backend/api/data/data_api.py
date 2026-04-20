from fastapi import APIRouter

router = APIRouter()


@router.get("/data", tags=["data"])
async def get_data() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/data/download_to_local", tags=["data"])
async def download_to_local():
    pass


@router.post("/data/upload_to_s3", tags=["data"])
async def upload_to_s3():
    pass


@router.get("/data/file_synced", tags=["data"])
async def file_synced():
    pass
