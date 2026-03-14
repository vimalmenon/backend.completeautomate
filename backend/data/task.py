from dataclasses import dataclass, field
from datetime import datetime
from functools import cached_property
from typing import Self
from uuid import UUID

from backend.data import PlatformDBData
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
    ref_id: str

    def to_dict(self) -> dict:
        return {"ref_id": self.ref_id}

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(ref_id=data["ref_id"])

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)


@dataclass
class YouTubeChannelVideoCheckerTaskData:
    ref_id: str
    poll_frequency_in_days: int = 3

    def to_dict(self) -> dict:
        return {
            "ref_id": self.ref_id,
            "poll_frequency_in_days": int(self.poll_frequency_in_days),
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            ref_id=data["ref_id"],
            poll_frequency_in_days=data.get("poll_frequency_in_days", 3),
        )

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)


@dataclass
class YouTubeVideoCheckerTaskData:
    ref_id: str
    poll_frequency_in_days: int = 3

    def to_dict(self) -> dict:
        return {
            "ref_id": self.ref_id,
            "poll_frequency_in_days": int(self.poll_frequency_in_days),
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            ref_id=data["ref_id"],
            poll_frequency_in_days=data.get("poll_frequency_in_days", 3),
        )

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)


@dataclass
class YouTubeChannelStatsUpdaterTaskData:
    ref_id: str
    poll_frequency_in_days: int = 3

    def to_dict(self) -> dict:
        return {
            "ref_id": self.ref_id,
            "poll_frequency_in_days": int(self.poll_frequency_in_days),
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            ref_id=data["ref_id"],
            poll_frequency_in_days=data.get("poll_frequency_in_days", 3),
        )

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)


@dataclass
class YouTubeVideoTaskData:
    ref_id: str
    comment: str | None = None

    def to_dict(self) -> dict:
        return {"ref_id": self.ref_id, "comment": self.comment}

    @classmethod
    def to_cls(cls, data):
        return cls(
            ref_id=data["ref_id"],
            comment=data.get("comment"),
        )


@dataclass
class YouTubeVideoStatsUpdaterTaskData:
    ref_id: str
    poll_frequency_in_days: int = 3

    def to_dict(self) -> dict:
        return {
            "ref_id": self.ref_id,
            "poll_frequency_in_days": self.poll_frequency_in_days,
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            ref_id=data["ref_id"],
            poll_frequency_in_days=data.get("poll_frequency_in_days", 3),
        )

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)
