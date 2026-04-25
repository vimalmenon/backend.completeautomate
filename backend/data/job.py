from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Self
from uuid import UUID

from backend.enum import JobsStatusEnum, JobTypeEnum


@dataclass
class JobData:
    id: UUID
    status: JobsStatusEnum
    type: JobTypeEnum
    task_data: dict
    description: str
    created_at: datetime
    failed_count: int = 0
    pending_on: list[UUID] = field(default_factory=list)
    completed_at: datetime | None = None
    error_msg: str | None = None

    def to_json(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "status": self.status.value,
            "type": self.type.value,
            "task_data": self.task_data,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "failed_count": self.failed_count,
            "pending_on": [str(job) for job in self.pending_on],
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "error_msg": self.error_msg,
        }

    @classmethod
    def to_cls(cls, data: dict[str, Any]) -> Self:
        return cls(
            id=UUID(data["id"]),
            status=JobsStatusEnum(data["status"]),
            type=JobTypeEnum(data["type"]),
            task_data=data["task_data"],
            description=data["description"],
            created_at=datetime.fromisoformat(data["created_at"]),
            failed_count=data.get("failed_count", 0),
            pending_on=[UUID(job) for job in data.get("pending_on", [])],
            completed_at=(
                datetime.fromisoformat(data["completed_at"])
                if data.get("completed_at")
                else None
            ),
            error_msg=data.get("error_msg"),
        )


@dataclass
class JobDataResponse:
    status: JobsStatusEnum
    failed_count: int = 0
    task_data: dict | None = None
    error_msg: str | None = None
    pending_on: list[UUID] = field(default_factory=list)
