from fastapi import APIRouter

router = APIRouter()


@router.get("/prompts", tags=["prompts"])
def list_prompts():
    pass
