from datetime import datetime
from uuid import UUID, uuid4

from pydantic import Field

from backend.data.api.base_model import BaseModelWithConfig
from backend.enum import AIModelEnum, PromptTaskEnum


class PromptRequest(BaseModelWithConfig):
    task: str
    description: str
    active_version: UUID
    prompt: str
    system_message: str
    ai: str
    comment: str | None = None
    last_updated: datetime
    prompt_data: list[dict] = Field(default_factory=list)


class PromptVersionResponse(BaseModelWithConfig):
    task: str
    version: UUID
    prompt: str
    system_message: str
    reflect_message: str
    ai: str
    created_at: datetime


class PromptVersionUpdateRequest(BaseModelWithConfig):
    prompt: str
    system_message: str
    ai: AIModelEnum


class PromptUpdateRequest(BaseModelWithConfig):
    description: str
    comment: str | None = None
    current_version: PromptVersionUpdateRequest


class PromptCreateRequest(BaseModelWithConfig):
    task: PromptTaskEnum
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
    examples: list[dict] = Field(default_factory=list)


class PromptRollbackResponse(BaseModelWithConfig):
    """Returned after a successful rollback — shows the restored prompt."""

    task: str
    version: UUID
    description: str
    prompt: str
    system_message: str
    ai: str
    comment: str | None = None
    last_updated: datetime
    rolled_back_from: UUID
    """The version that was active before the rollback."""
