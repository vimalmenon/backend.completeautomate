from fastapi import APIRouter, HTTPException

from backend.data.api import (
    PromptCreateRequest,
    PromptRequest,
    PromptUpdateRequest,
    PromptUpdateResult,
)
from backend.data.api.prompt import PromptVersionResponse
from backend.enum import PromptTaskEnum
from backend.manager import PromptManager

router = APIRouter()


@router.get("/prompts", tags=["prompts"])
async def list_prompts():
    prompts = PromptManager().get_prompts()
    return [PromptRequest.model_validate(prompt.to_json()) for prompt in prompts]


@router.get("/prompts/{task}", tags=["prompts"])
async def get_prompt(task: PromptTaskEnum):
    prompt = PromptManager().get_prompt_by_task(task)
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return PromptRequest.model_validate(prompt.to_json())


@router.post("/prompts", tags=["prompts"])
async def create_prompt(data: PromptCreateRequest):
    prompt = PromptManager().add_prompt(
        data=PromptUpdateResult(
            task=data.task,
            description=data.description,
            comment=data.comment,
            prompt=data.current_version.prompt,
            system_message=data.current_version.system_message,
            ai=data.current_version.ai,
        )
    )
    return PromptRequest.model_validate(prompt.to_json())


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


@router.get("/prompts/{task}/versions", tags=["prompts"])
async def list_versions(task: PromptTaskEnum):
    versions = PromptManager().get_version_history(task)
    return [PromptVersionResponse.model_validate(v.to_json()) for v in versions]


@router.get("/prompts/{task}/results", tags=["prompts"])
async def list_results(task: PromptTaskEnum):
    results = PromptManager().get_results(task)
    return [r.to_json() for r in results]
