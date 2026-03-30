from dataclasses import dataclass
from functools import cached_property
from typing import Self

from backend.data import PlatformDBData
from backend.enum import (
    YouTubeVideoTaskEnum,
)


@dataclass
class YouTubeChannelTaskData:
    ref_id: str

    def to_dict(self) -> dict:
        return {
            "ref_id": self.ref_id,
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            ref_id=data["ref_id"],
        )

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
            poll_frequency_in_days=int(data.get("poll_frequency_in_days", 3)),
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
            poll_frequency_in_days=int(data.get("poll_frequency_in_days", 3)),
        )

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)


@dataclass
class YouTubeStatsUpdaterTaskData:
    poll_frequency_in_days: int

    @classmethod
    def to_cls(cls, data) -> Self:
        return cls(poll_frequency_in_days=int(data["poll_frequency_in_days"]))

    def to_json(self) -> dict:
        return {"poll_frequency_in_days": self.poll_frequency_in_days}


@dataclass
class YouTubeVideoTaskData:
    ref_id: str
    task: YouTubeVideoTaskEnum = YouTubeVideoTaskEnum.YouTubeVideoStart
    user_video_comment: str | None = None

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            ref_id=data["ref_id"],
            task=YouTubeVideoTaskEnum(data["task"]),
            user_video_comment=data.get("user_video_comment"),
        )

    def to_json(self) -> dict:
        return {
            "ref_id": self.ref_id,
            "task": self.task.value,
            "user_video_comment": self.user_video_comment,
        }

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)


@dataclass
class YouTubeVideoStatsUpdaterTaskData:
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
            poll_frequency_in_days=int(data.get("poll_frequency_in_days", 3)),
        )

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)
