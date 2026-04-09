from fastapi import APIRouter

from backend.manager import PromptManager

router = APIRouter()


@router.get("/prompts", tags=["prompts"])
async def list_prompts():
    return PromptManager().get_prompts()
