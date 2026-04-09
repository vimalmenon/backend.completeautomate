from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from backend.data.api.base_mode import BaseModelWithConfig
from backend.enum import JobsStatusEnum, JobTypeEnum


class JobResponse(BaseModelWithConfig):

    id: UUID
    status: JobsStatusEnum
    type: JobTypeEnum
    task_data: dict[str, Any]
    description: str
    created_at: datetime
    failed_count: int = 0
    pending_on: list[UUID] = Field(default_factory=list)
    completed_at: datetime | None = None
    error_msg: str | None = None
