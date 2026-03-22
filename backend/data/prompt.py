from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any, Self

from backend.enum import AIImageModelEnum, AIModelEnum, PromptTaskEnum, TeamEnum


@dataclass
class PromptVersionDBData:
    prompt: str
    system_message: str
    version: str

    def to_json(self) -> dict:
        return {
            "prompt": self.prompt,
            "system_message": self.system_message,
            "version": self.version,
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            prompt=data["prompt"],
            system_message=data["system_message"],
            version=data["version"],
        )


@dataclass
class PromptDBData:
    prompt: str
    system_message: str
    task: PromptTaskEnum
    role: TeamEnum
    describe: str
    prompt_data: PromptVersionDBData
    ai: AIModelEnum | AIImageModelEnum
    version: str = "LATEST"
    last_updated: datetime = datetime.now()

    def get_agent_name(self) -> str:
        return self.role.display_name

    def to_json(self) -> dict:

        return {
            "prompt": self.prompt,
            "system_message": self.system_message,
            "task": self.task.value,
            "role": self.role.role,
            "ai": self.ai.value,
            "describe": self.describe,
            "version": self.version,
            "prompt_data": self.prompt_data.to_json(),
            "last_updated": self.last_updated.isoformat(),
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            prompt=data["prompt"],
            system_message=data["system_message"],
            task=PromptTaskEnum(data["task"]),
            role=TeamEnum.from_value(data["role"]),
            ai=AIModelEnum(data["ai"]),
            version=data.get("version", "LATEST"),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            # TODO Remove get after transformation
            describe=data.get("describe", ""),
            prompt_data=PromptVersionDBData.to_cls(data.get("prompt_data", {})),
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
class PromptSuggesterDBData:
    task: PromptTaskEnum
    description: str
    versions: list[PromptVersionDBData]
    comment: str | None

    def to_json(self) -> dict:
        return {
            "task": self.task.value,
            "description": self.description,
            "comment": self.comment,
            "versions": [version.to_json() for version in self.versions],
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            task=PromptTaskEnum(data["task"]),
            description=data["description"],
            comment=data.get("comment"),
            versions=[
                PromptVersionDBData.to_cls(version)
                for version in data.get("versions", [])
            ],
        )


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
