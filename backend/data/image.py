from dataclasses import dataclass
from functools import cached_property
from typing import Optional, Self
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
    model: Optional[str] = None  # Optional model selection (e.g., "GROK", "FLUX")

    def to_json(self) -> dict:
        json_data = {
            "id": str(self.id),
            "prompt": self.prompt,
            "name": self.name,
            "task_id": str(self.task_id),
            "image_type": self.image_type.value,
            "data": self.data.to_json(),
            "ref_id": self.ref_id,
        }
        if self.model:
            json_data["model"] = self.model
        return json_data

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
            model=data.get("model"),  # Optional model parameter
        )


@dataclass
class ImagePromptData:
    name: str
    description: str
    prompt: str
    negative_prompt: str | None = None
    status: JobStatusEnum = JobStatusEnum.NEW

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "prompt": self.prompt,
            "description": self.description,
            "status": self.status.value,
            "negative_prompt": self.negative_prompt,
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            name=data["name"],
            prompt=data["prompt"],
            description=data["description"],
            status=JobStatusEnum(data.get("status", JobStatusEnum.NEW.value)),
            negative_prompt=data.get("negative_prompt"),
        )


@dataclass
class ImagePromptJobData:
    task_id: UUID
    description: str
    ref_id: str
    image_type: ImageTypeEnum

    @property
    def name(self) -> str:
        return self.__class__.__name__

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
        )

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)
