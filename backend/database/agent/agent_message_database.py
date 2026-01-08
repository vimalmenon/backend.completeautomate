from backend.data import MessageDBData
from backend.database.dynamo_database import DbManager
from backend.enum.db_keys import DbKeysEnum


class AgentMessageDB:
    TABLE = "CA#AGENT_MESSAGES"

    def __init__(self):
        self.db_manager = DbManager()

    def save_message(self, data: MessageDBData):
        self.db_manager.add_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: data.task_id,
                **data.to_json(),
            }
        )

    def get_messages_by_task_id(self, task_id: str) -> MessageDBData | None:
        item = self.db_manager.get_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: task_id,
            }
        )
        if item:
            return MessageDBData.to_cls(item)
        return None

    def update_message(self, data: MessageDBData):
        pass
