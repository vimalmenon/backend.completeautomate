from dataclasses import dataclass, field
from datetime import datetime
from typing import Self


@dataclass
class MessageDBData:
    task_id: str
    messages: list[dict] = field(default_factory=list)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_json(self) -> dict:
        return {
            "task_id": self.task_id,
            "messages": self.messages,
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            task_id=data.get("task_id", ""),
            messages=data.get("messages", []),
            updated_at=datetime.fromisoformat(
                data.get("updated_at", datetime.now().isoformat())
            ),
        )
