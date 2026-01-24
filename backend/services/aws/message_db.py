from backend.services.aws.dynamo_database import DbManager
from dataclasses import dataclass
from backend.services.data.enum import DbKeys
from boto3.dynamodb.conditions import Key
from uuid import uuid4, UUID


@dataclass
class Message:
    name: str
    content: str
    messages: list[dict]
    ref_id: UUID
    llm_model: str | None
    completed: bool = False
    id: str | None = None

    @classmethod
    def to_cls(cls, data: dict):
        return cls(
            name=data["name"],
            content=data["content"],
            messages=data["messages"],
            completed=data.get("completed", False),
            llm_model=data.get("llm_model", None),
            id=data.get("id", None),
            ref_id=UUID(data["ref_id"]),
        )

    def to_json(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "content": self.content,
            "messages": self.messages,
            "completed": self.completed,
            "llm_model": self.llm_model,
            "ref_id": str(self.ref_id),
        }


class MessageDB:
    table = "CA#MESSAGE"

    def __init__(self) -> None:
        self.db_manager = DbManager()

    def save_message(self, message: Message) -> None:
        try:
            self.db_manager.add_item(
                {
                    DbKeys.Primary.value: self.table,
                    DbKeys.Secondary.value: message.name,
                    **message.to_json(),
                }
            )
        except Exception:
            pass

    def save_message_from_agent_result(self, result: dict) -> None:
        message = self.__transform_result_to_message(result)
        self.save_message(message)

    def get_message(self) -> None:
        pass

    def query_messages(self) -> None:
        try:
            results = self.db_manager.query_items(
                Key(DbKeys.Primary.value).eq(self.table)
            )
            return [Message.to_cls(item) for item in results]
        except Exception:
            return []

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
            content=message.content,
            messages=[msg.dict() for msg in messages],
            llm_model=message.response_metadata.get("model_name"),
            completed=False,
            ref_id=uuid4(),
        )
        return message
