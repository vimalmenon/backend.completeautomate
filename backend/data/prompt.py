from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any, Self

from backend.enum import AIImageModelEnum, AIModelEnum, PromptTaskEnum, TeamEnum


@dataclass
class PromptVersionDBData:
    prompt: str
    system_message: str
    version: int
    comment: str

    def to_json(self) -> dict:
        return {
            "prompt": self.prompt,
            "system_message": self.system_message,
            "version": int(self.version),
            "comment": self.comment,
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            prompt=data["prompt"],
            system_message=data["system_message"],
            version=int(data["version"]),
            comment=data["comment"],
        )


@dataclass
class PromptDBData:
    prompt: str
    system_message: str
    task: PromptTaskEnum
    role: TeamEnum
    description: str
    versions: list[PromptVersionDBData]
    ai: AIModelEnum | AIImageModelEnum
    use_version: int
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
            "description": self.description,
            "use_version": self.use_version,
            "versions": [version.to_json() for version in self.versions],
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
            use_version=int(data["use_version"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            description=data["description"],
            versions=[
                PromptVersionDBData.to_cls(version) for version in data["versions"]
            ],
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
