from backend.services.aws.dynamo_database import DbManager
from dataclasses import dataclass
from backend.services.data.enum import DbKeys


@dataclass
class Message:
    name: str
    content: str
    messages: list[dict]
    llm_model: str | None
    completed: bool = False

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            name=data["name"],
            content=data["content"],
            messages=data["messages"],
            completed=data.get("completed", False),
            llm_model=data.get("llm_model", None),
        )

    def to_json(self) -> dict:
        return {
            "name": self.name,
            "content": self.content,
            "messages": self.messages,
            "completed": self.completed,
            "llm_model": self.llm_model,
        }


class MessageDB:
    table = "CA#MESSAGE"
    def __init__(self) -> None:
        self.db_manager = DbManager()

    def save_message(self, message: Message) -> None:
        breakpoint()
        try:
            self.db_manager.add_item({
                DbKeys.Primary.value: self.table,
                DbKeys.Secondary.value: message.name,
                **message.to_json()
            })
        except Exception as e:
            breakpoint()
        

    def get_message(self) -> None:
        pass

    def delete_message(self) -> None:
        pass
