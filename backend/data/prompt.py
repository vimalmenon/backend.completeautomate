from dataclasses import dataclass
from datetime import datetime
from typing import Self

from backend.enum import AIModelEnum, PromptTaskEnum, TeamEnum


@dataclass
class PromptDBData:
    prompt: str
    system_message: str
    task: PromptTaskEnum
    role: TeamEnum
    ai: AIModelEnum
    version: str = "LATEST"
    last_updated: datetime = datetime.now()

    def to_json(self) -> dict:
        return {
            "prompt": self.prompt,
            "system_message": self.system_message,
            "task": self.task.value,
            "role": self.role.role,
            "ai": self.ai.value,
            "version": self.version,
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
        )


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
class PromptSuggesterDBData:
    ref_id: str
    description: str
    versions: list[PromptVersionDBData]
    comment: str | None

    def to_json(self) -> dict:
        return {
            "ref_id": self.ref_id,
            "description": self.description,
            "comment": self.comment,
            "versions": [version.to_json() for version in self.versions],
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            ref_id=data["ref_id"],
            description=data["description"],
            comment=data.get("comment"),
            versions=[
                PromptVersionDBData.to_cls(version)
                for version in data.get("versions", [])
            ],
        )
