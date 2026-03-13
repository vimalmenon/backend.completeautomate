from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID

from backend.enum import JobEnum, TaskStatusEnum


@dataclass
class TaskData:
    id: UUID
    job_type: JobEnum
    payload: dict
    created_at: datetime
    status: TaskStatusEnum
    failed_count: int = 0
    trail: list[UUID] = field(default_factory=list)
    completed_at: datetime | None = None

    def to_json(self) -> dict:
        return {
            "id": str(self.id),
            "job_type": self.job_type.value,
            "payload": self.payload,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "failed_count": self.failed_count,
            "trail": [str(trail) for trail in self.trail],
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            id=UUID(data["id"]),
            job_type=JobEnum(data["job_type"]),
            payload=data["payload"],
            created_at=datetime.fromisoformat(data["created_at"]),
            status=TaskStatusEnum(data["status"]),
            failed_count=data.get("failed_count", 0),
            trail=[UUID(trail) for trail in data["trail"]],
            completed_at=(
                datetime.fromisoformat(data["completed_at"])
                if data["completed_at"]
                else None
            ),
        )


@dataclass
class YouTubeChannelTaskData:
    channel_id: str

    def to_dict(self) -> dict:
        return {"channel_id": self.channel_id}

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(channel_id=data["channel_id"])


@dataclass
class YouTubeVideoTaskData:
    pass
