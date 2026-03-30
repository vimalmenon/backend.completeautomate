from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Any, Self
from uuid import UUID

from backend.enum import AIModelEnum, PromptTaskEnum
from backend.exception.app_exception import AppException


@dataclass
class PromptVersionDBData:
    prompt: str
    system_message: str
    version: UUID
    ai: AIModelEnum
    created_at: datetime = datetime.now()

    def to_json(self) -> dict:
        return {
            "prompt": self.prompt,
            "system_message": self.system_message,
            "version": str(self.version),
            "ai": self.ai.value,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            prompt=data["prompt"],
            system_message=data["system_message"],
            version=UUID(data["version"]),
            ai=AIModelEnum(data["ai"]),
            created_at=datetime.fromisoformat(data["created_at"]),
        )


@dataclass
class PromptDBData:
    task: PromptTaskEnum
    description: str
    versions: list[PromptVersionDBData]
    version: UUID
    comment: str | None = None
    last_updated: datetime = datetime.now()
    prompt_data: list[dict] = field(default_factory=list)

    def __post_init__(self):
        selected_prompts = [
            version for version in self.versions if version.version == self.version
        ]
        if len(selected_prompts) == 1:
            self.prompt = selected_prompts[0].prompt
            self.system_message = selected_prompts[0].system_message
            self.ai = selected_prompts[0].ai
        else:
            raise AppException("Cannot find prompt for this version")

    def to_json(self) -> dict:
        return {
            "task": self.task.value,
            "version": str(self.version),
            "description": self.description,
            "versions": [version.to_json() for version in self.versions],
            "comment": self.comment,
            "last_updated": self.last_updated.isoformat(),
            "prompt_data": self.prompt_data,
        }

    def add_prompt_version(self, data: PromptVersionDBData) -> Self:
        self.versions.append(data)
        return self

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            task=PromptTaskEnum(data["task"]),
            version=UUID(data["version"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            versions=[
                PromptVersionDBData.to_cls(version) for version in data["versions"]
            ],
            comment=data.get("comment"),
            description=data["description"],
            prompt_data=data["prompt_data"],
        )

    def copy(self) -> Self:
        """Create a shallow copy of this PromptDBData object."""
        return replace(self)

    def values_to_update(self, result: Self) -> dict[str, Any]:
        updated_values: dict[str, Any] = {}
        if self.ai != result.ai:
            updated_values["ai"] = self.ai
        return updated_values


@dataclass
class YouTubeThumbnailImageGenerationPromptData:
    title: str
    description: str
    video_summary: str

    def to_json(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "video_summary": self.video_summary,
        }
