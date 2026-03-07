from dataclasses import dataclass, field
from functools import cached_property
from typing import Self
from uuid import UUID

from backend.data.platform import PlatformDBData
from backend.data.s3 import S3Data
from backend.enum import (
    ImageTypeEnum,
    JobStatusEnum,
)


@dataclass
class ImageGeneratorJobData:
    id: UUID
    name: str
    prompt: str
    image_type: ImageTypeEnum
    ref_id: str
    task_id: UUID
    data: S3Data

    def to_json(self) -> dict:
        return {
            "id": str(self.id),
            "prompt": self.prompt,
            "name": self.name,
            "task_id": str(self.task_id),
            "image_type": self.image_type.value,
            "data": self.data.to_json(),
            "ref_id": self.ref_id,
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            id=UUID(data["id"]),
            name=data["name"],
            prompt=data["prompt"],
            task_id=UUID(data["task_id"]),
            image_type=ImageTypeEnum(data["image_type"]),
            data=S3Data.to_cls(data["data"]),
            ref_id=data["ref_id"],
        )


@dataclass
class PromptData:
    name: str
    prompt: str
    description: str
    status: JobStatusEnum = JobStatusEnum.NEW

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "prompt": self.prompt,
            "description": self.description,
            "status": self.status.value,
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            name=data["name"],
            prompt=data["prompt"],
            description=data["description"],
            status=JobStatusEnum(data.get("status", JobStatusEnum.NEW.value)),
        )


@dataclass
class ImagePromptJobData:
    task_id: UUID
    description: str
    ref_id: str
    image_type: ImageTypeEnum
    name: str = "ImagePromptJobData"

    def to_json(self) -> dict:
        return {
            "task_id": str(self.task_id),
            "description": self.description,
            "image_type": self.image_type.value,
            "ref_id": self.ref_id,
            "name": self.name,
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            task_id=UUID(data["task_id"]),
            description=data["description"],
            image_type=ImageTypeEnum(data["image_type"]),
            ref_id=data["ref_id"],
            name=data.get("name", cls.__name__),
        )

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)


@dataclass
class ImagePromptDBData:
    id: UUID
    task_id: UUID
    ref_id: str
    comment: str | None = None
    status: JobStatusEnum = JobStatusEnum.NEW
    prompts: list[PromptData] = field(default_factory=list)

    def to_json(self) -> dict:
        return {
            "id": str(self.id),
            "task_id": str(self.task_id),
            "comment": self.comment,
            "status": self.status.value,
            "prompts": [pr.to_json() for pr in self.prompts],
            "ref_id": self.ref_id,
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            id=UUID(data["id"]),
            task_id=UUID(data["task_id"]),
            comment=data.get("comment"),
            prompts=[PromptData.to_cls(pr) for pr in data.get("prompts", [])],
            ref_id=data["ref_id"],
        )

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)
