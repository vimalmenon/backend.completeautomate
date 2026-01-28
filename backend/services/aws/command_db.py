from backend.services.aws.dynamo_database import DbManager
from dataclasses import dataclass
from uuid import uuid4, UUID
from datetime import datetime, timezone
from backend.services.exception.app_exception import AppException
from backend.services.data.enum import DbKeys


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

    def save_command(self, command: Command) -> dict:
        try:
            self.db_manager.add_item(
                {
                    DbKeys.Primary.value: self.table,
                    DbKeys.Secondary.value: str(command.id),
                    **command.to_json(),
                }
            )
        except Exception as e:
            raise AppException(f"Error saving command: {e}")
        return {
            DbKeys.Primary.value: self.table,
            DbKeys.Secondary.value: str(command.id),
        }
