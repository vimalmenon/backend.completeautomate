from fastapi import APIRouter

from backend.data.api import PromptRequest
from backend.manager import PromptManager

router = APIRouter()


@router.get("/prompts", tags=["prompts"])
async def list_prompts():
    prompts = PromptManager().get_prompts()
    return [PromptRequest.model_validate(prompt.to_json()) for prompt in prompts]
