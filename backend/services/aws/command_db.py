from backend.services.aws.dynamo_database import DbManager
from dataclasses import dataclass
from uuid import uuid4, UUID
from datetime import datetime, timezone


@dataclass
class Command:
    id: UUID
    cmd: str
    created_at: datetime

    def to_json(self) -> dict:
        return {
            "id": str(self.id),
            "cmd": self.cmd,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def to_cls(cls, data: dict):
        return cls(
            id=UUID(data["id"]),
            cmd=data["cmd"],
            created_at=datetime.fromisoformat(data["created_at"]),
        )


class CommandDB:
    table = "CA#COMMAND"

    def __init__(self):
        self.db_manager = DbManager()

    def save_command(self, command: Command) -> None:
        try:
            self.db_manager.add_item(
                command.to_json(),
                table_name=self.table,
            )
        except Exception as e:
            print(f"Error saving command: {e}")
