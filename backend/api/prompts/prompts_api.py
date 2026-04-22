from fastapi import APIRouter

from backend.data.api import PromptRequest, PromptUpdateRequest, PromptUpdateResult
from backend.enum import PromptTaskEnum
from backend.manager import PromptManager

router = APIRouter()


@router.get("/prompts", tags=["prompts"])
async def list_prompts():
    prompts = PromptManager().get_prompts()
    return [PromptRequest.model_validate(prompt.to_json()) for prompt in prompts]


@router.put("/prompts/{task}", tags=["prompts"])
async def update_prompt(task: PromptTaskEnum, data: PromptUpdateRequest):
    prompt = PromptManager().update_prompt(
        task=task,
        data=PromptUpdateResult(
            task=task,
            description=data.description,
            comment=data.comment,
            prompt=data.current_version.prompt,
            system_message=data.current_version.system_message,
            ai=data.current_version.ai,
        ),
    )
    return PromptRequest.model_validate(prompt.to_json())
