from datetime import datetime
from uuid import UUID, uuid4

from pydantic import Field

from backend.data.api.base_model import BaseModelWithConfig
from backend.data.prompt import PromptVersionDBData
from backend.enum import AIModelEnum, PromptTaskEnum


class PromptRequest(BaseModelWithConfig):
    task: str
    description: str
    version: UUID
    last_updated: datetime
    versions: list[PromptVersionDBData]
    comment: str | None = None
    prompt_data: list[dict] = Field(default_factory=list)


class PromptVersionUpdateRequest(BaseModelWithConfig):
    prompt: str
    system_message: str
    ai: AIModelEnum


class PromptUpdateRequest(BaseModelWithConfig):
    description: str
    comment: str | None = None
    current_version: PromptVersionUpdateRequest


class PromptUpdateResult(BaseModelWithConfig):
    task: PromptTaskEnum
    description: str
    comment: str | None = None
    prompt: str
    system_message: str
    ai: AIModelEnum
    version: UUID = Field(default_factory=uuid4)
