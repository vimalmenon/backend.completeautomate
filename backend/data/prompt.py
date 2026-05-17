from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID

from backend.enum import AIModelEnum, PromptTaskEnum


@dataclass
class PromptDBData:
    """Main prompt definition — only the ACTIVE version stored inline."""

    task: PromptTaskEnum
    description: str
    active_version: UUID
    prompt: str
    system_message: str
    ai: AIModelEnum
    comment: str | None = None
    last_updated: datetime = datetime.now()
    prompt_data: list[dict] = field(default_factory=list)

    def to_json(self) -> dict:
        return {
            "task": self.task.value,
            "description": self.description,
            "active_version": str(self.active_version),
            "prompt": self.prompt,
            "system_message": self.system_message,
            "ai": self.ai.value,
            "comment": self.comment,
            "last_updated": self.last_updated.isoformat(),
            "prompt_data": self.prompt_data,
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            task=PromptTaskEnum(data["task"]),
            description=data["description"],
            active_version=UUID(data["active_version"]),
            prompt=data["prompt"],
            system_message=data["system_message"],
            ai=AIModelEnum(data["ai"]),
            comment=data.get("comment"),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            prompt_data=data.get("prompt_data", []),
        )


@dataclass
class PromptVersionDBData:
    """One item per version — full history, separate from the active prompt."""

    task: PromptTaskEnum
    version: UUID
    prompt: str
    system_message: str
    reflect_message: str
    ai: AIModelEnum
    created_at: datetime = datetime.now()

    def to_json(self) -> dict:
        return {
            "task": self.task.value,
            "version": str(self.version),
            "prompt": self.prompt,
            "system_message": self.system_message,
            "reflect_message": self.reflect_message,
            "ai": self.ai.value,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            task=PromptTaskEnum(data["task"]),
            version=UUID(data["version"]),
            prompt=data["prompt"],
            system_message=data["system_message"],
            reflect_message=data.get("reflect_message", ""),
            ai=AIModelEnum(data["ai"]),
            created_at=datetime.fromisoformat(data["created_at"]),
        )


@dataclass
class PromptResultDBData:
    """One item per evaluation run."""

    task: PromptTaskEnum
    result_id: UUID
    version: UUID
    response: str
    score: int | None
    prompt_data_snapshot: dict
    created_at: datetime = datetime.now()

    def to_json(self) -> dict:
        return {
            "task": self.task.value,
            "result_id": str(self.result_id),
            "version": str(self.version),
            "response": self.response,
            "score": self.score,
            "prompt_data_snapshot": self.prompt_data_snapshot,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            task=PromptTaskEnum(data["task"]),
            result_id=UUID(data["result_id"]),
            version=UUID(data["version"]),
            response=data["response"],
            score=data.get("score"),
            prompt_data_snapshot=data.get("prompt_data_snapshot", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
        )
