from datetime import datetime
from typing import Any
from uuid import UUID

import humps
from pydantic import BaseModel, ConfigDict, Field

from backend.enum import JobsStatusEnum, JobTypeEnum


class JobData(BaseModel):
    model_config = ConfigDict(
        alias_generator=humps.camelize,
        populate_by_name=True,
        serialize_by_alias=True,
        use_enum_values=True,
    )

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
