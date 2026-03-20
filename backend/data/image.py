from dataclasses import dataclass
from functools import cached_property
from typing import Self
from uuid import UUID

from backend.data.platform import PlatformDBData
from backend.enum import (
    ImageTypeEnum,
)


@dataclass
class ImagePromptData:
    name: str
    description: str
    prompt: str
    negative_prompt: str | None = None
    selected: bool = False

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "prompt": self.prompt,
            "description": self.description,
            "negative_prompt": self.negative_prompt,
            "selected": self.selected,
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            name=data["name"],
            prompt=data["prompt"],
            description=data["description"],
            negative_prompt=data.get("negative_prompt"),
            selected=data.get("selected", False),
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
