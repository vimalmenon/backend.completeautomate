from backend.services.aws.dynamo_database import DbManager
from dataclasses import dataclass
from backend.services.data.enum import DbKeys
from boto3.dynamodb.conditions import Key
from uuid import uuid4, UUID
from backend.config.enum import TeamEnum
from datetime import datetime, timezone
from backend.services.exception.app_exception import AppException


@dataclass
class Message:
    name: str
    agent: str
    content: str
    messages: list[dict]
    ref_id: dict
    created_at: datetime
    llm_model: str | None
    completed: bool = False
    id: str | None = None

    @classmethod
    def to_cls(cls, data: dict):
        return cls(
            name=data["name"],
            agent=data["agent"],
            content=data["content"],
            messages=data["messages"],
            completed=data.get("completed", False),
            llm_model=data.get("llm_model", None),
            id=data.get("id", None),
            ref_id=data["ref_id"],
            created_at=datetime.now(timezone.utc),
        )

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "agent": self.agent,
            "content": self.content,
            "messages": self.messages,
            "completed": self.completed,
            "llm_model": self.llm_model,
            "ref_id": self.ref_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class MessageDB:
    table = "CA#MESSAGE"

    def __init__(self, team: TeamEnum) -> None:
        self.db_manager = DbManager()
        self.team = team

    def save_message(self, message: Message) -> None:
        try:
            self.db_manager.add_item(
                {
                    DbKeys.Primary.value: self.table,
                    DbKeys.Secondary.value: message.name,
                    **message.to_json(),
                }
            )
        except Exception as e:
            raise AppException(f"Error saving message: {e}")

    def save_message_from_agent_result(self, result: dict) -> None:
        message = self.__transform_result_to_message(result)
        self.save_message(message)

    def get_message(self) -> None:
        pass

    def get_message_by_ref_id(self, ref_id: UUID) -> list[Message] | None:
        try:
            results = self.db_manager.query_items(
                Key(DbKeys.Primary.value).eq(self.table) & Key("ref_id").eq(str(ref_id))
            )
            if results:
                return [
                    Message.to_cls({**item, "agent": self.team.value})
                    for item in results
                ]
            return None
        except Exception as e:
            raise AppException(f"Error getting message by ref_id: {e}")

    def query_messages(self) -> list[Message]:
        try:
            results = self.db_manager.query_items(
                Key(DbKeys.Primary.value).eq(self.table)
            )
            return [
                Message.to_cls({**item, "agent": self.team.value}) for item in results
            ]
        except Exception as e:
            raise AppException(f"Error querying messages: {e}")

    def delete_message(self, id: str) -> None:
        self.db_manager.remove_item(
            {
                DbKeys.Primary.value: self.table,
                DbKeys.Secondary.value: id,
            }
        )

    def __transform_result_to_message(self, result) -> Message:
        message = result.get("messages", [])[-1]
        messages = result.get("messages", [])
        message = Message(
            name=message.name,
            agent=self.team.value,
            content=message.content,
            messages=[msg.dict() for msg in messages],
            llm_model=message.response_metadata.get("model_name"),
            completed=False,
            ref_id={},
            created_at=datetime.now(timezone.utc),
        )
        return message
