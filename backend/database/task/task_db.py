import logging

from boto3.dynamodb.conditions import Attr, Key

from backend.data import TaskData
from backend.database import DbManager
from backend.enum.db_keys import DbKeysEnum
from backend.enum.status import TaskStatusEnum

logger = logging.getLogger(__name__)


class TaskDB:
    TABLE = "CA#TASK"

    def __init__(self):
        self.db_manager = DbManager()

    def add_task(self, task: TaskData):
        logger.info(f"Adding task with id: {task.id}")
        self.db_manager.add_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: str(task.id),
                **task.to_json(),
            }
        )

    def update_task(self, task: TaskData):
        logger.info(f"Updating task with id: {task.id}")
        self.__update_task(task)

    def get_tasks(self) -> list[TaskData]:
        logger.info("Fetching all tasks")
        items = self.db_manager.query_items(
            Key(DbKeysEnum.Primary.value).eq(self.TABLE)
        )
        return [TaskData.to_cls(item) for item in items]

    def get_task_by_id(self, task_id: str) -> TaskData | None:
        logger.info(f"Fetching task with id: {task_id}")
        item = self.db_manager.get_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: str(task_id),
            }
        )
        if item:
            return TaskData.to_cls(item)
        return None

    def get_active_tasks(self) -> list[TaskData]:
        logger.info("Fetching active tasks")
        items = self.db_manager.query_items(
            Key(DbKeysEnum.Primary.value).eq(self.TABLE),
            filter_expression=Attr("status").is_in(
                [TaskStatusEnum.IN_PROGRESS.value, TaskStatusEnum.FAILED.value]
            ),
        )
        return [TaskData.to_cls(item) for item in items]

    def delete_task(self, task: TaskData):
        logger.info(f"Deleting task with id: {task.id}")
        self.db_manager.remove_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: str(task.id),
            }
        )

    def query_items(self, task_status: TaskStatusEnum) -> list[TaskData]:
        logger.info(f"Querying tasks with status: {task_status.value}")
        items = self.db_manager.query_items(
            Key(DbKeysEnum.Primary.value).eq(self.TABLE),
            filter_expression=Attr("status").eq(task_status.value),
        )
        return [TaskData.to_cls(item) for item in items]

    def __update_task(self, task: TaskData) -> None:
        logger.info(
            f"Updating task status to {task.status.value} for task id: {task.id}"
        )
        # key = {
        #     DbKeysEnum.Primary.value: self.TABLE,
        #     DbKeysEnum.Secondary.value: str(task.id),
        # }
        # self.db_manager.update_data(
        #     key=key,
        #     data={
        #         "status": task.status.value,
        #         "completed_at": (
        #             task.completed_at.isoformat() if task.completed_at else None
        #         ),
        #         "failed_count": task.failed_count,
        #     },
        # )

        update_expression = [
            "#status = :status",
            "failed_count = :failed_count",
            "completed_at = :completed_at",
        ]
        expression_attribute_values = {
            ":status": task.status.value,
            ":completed_at": (
                task.completed_at.isoformat() if task.completed_at else None
            ),
            ":failed_count": task.failed_count,
        }
        self.db_manager.update_item(
            Key={
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: str(task.id),
            },
            UpdateExpression=f"SET {', '.join(update_expression)}",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues=expression_attribute_values,
        )

    def update_data(self, key: dict, values: dict) -> None:
        update_expression, expression_attribute_names, expression_attribute_values = (
            self.db_manager.get_update_values(values)
        )
        self.db_manager.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
        )
