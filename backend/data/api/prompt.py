from datetime import datetime
from uuid import UUID

from pydantic import Field

from backend.data.api.base_mode import BaseModelWithConfig
from backend.data.prompt import PromptVersionDBData


class PromptRequest(BaseModelWithConfig):
    task: str
    description: str
    version: UUID
    last_updated: datetime
    versions: list[PromptVersionDBData]
    comment: str | None = None
    prompt_data: list[dict] = Field(default_factory=list)
