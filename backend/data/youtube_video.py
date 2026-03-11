from dataclasses import dataclass
from functools import cached_property
from typing import Self

from backend.data.platform import PlatformDBData


@dataclass
class YouTubeVideoReviewerJobData:
    ref_id: str
    transcript: str

    def to_json(self) -> dict:
        return {"ref_id": self.ref_id, "transcript": self.transcript}

    @classmethod
    def to_cls(cls, data) -> Self:
        return cls(ref_id=data["ref_id"], transcript=data["transcript"])

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)


@dataclass
class YouTubeVideoReviewerDBData:
    ref_id: str
    task_id: str
    downsides: list[str]
    upsides: list[str]

    def to_json(self) -> dict:
        return {
            "ref_id": self.ref_id,
            "task_id": self.task_id,
            "downsides": self.downsides,
            "upsides": self.upsides,
        }

    @classmethod
    def to_cls(cls, data) -> Self:
        return cls(
            ref_id=data["ref_id"],
            task_id=data["task_id"],
            downsides=data["downsides"],
            upsides=data["upsides"],
        )

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)
