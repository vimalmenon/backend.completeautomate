import logging

from boto3.dynamodb.conditions import Attr, Key

from backend.data import Task
from backend.database import DbManager
from backend.enum.db_keys import DbKeysEnum
from backend.enum.status import TaskStatusEnum

logger = logging.getLogger(__name__)


class TaskDB:
    TABLE = "CA#TASK"

    def __init__(self):
        self.db_manager = DbManager()

    def add_task(self, task: Task):
        logger.info(f"Adding task with id: {task.id}")
        self.db_manager.add_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: str(task.id),
                **task.to_json(),
            }
        )

    def update_task(self, task: Task):
        logger.info(f"Updating task with id: {task.id}")
        self.__update_task(task)

    def get_tasks(self) -> list[Task]:
        logger.info("Fetching all tasks")
        items = self.db_manager.query_items(
            Key(DbKeysEnum.Primary.value).eq(self.TABLE)
        )
        return [Task.to_cls(item) for item in items]

    def get_task_by_id(self, task_id: str) -> Task | None:
        logger.info(f"Fetching task with id: {task_id}")
        item = self.db_manager.get_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: str(task_id),
            }
        )
        if item:
            return Task.to_cls(item)
        return None

    def get_active_tasks(self) -> list[Task]:
        logger.info("Fetching active tasks")
        items = self.db_manager.query_items(
            Key(DbKeysEnum.Primary.value).eq(self.TABLE),
            filter_expression=Attr("status").is_in(
                [TaskStatusEnum.IN_PROGRESS.value, TaskStatusEnum.FAILED.value]
            ),
        )
        return [Task.to_cls(item) for item in items]

    def delete_task(self, task: Task):
        logger.info(f"Deleting task with id: {task.id}")
        self.db_manager.remove_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: str(task.id),
            }
        )

    def cleanup_tasks(self) -> None:
        logger.info("Starting cleanup of tasks with CLEAN_UP status")
        items = self.db_manager.query_items(
            Key(DbKeysEnum.Primary.value).eq(self.TABLE),
            filter_expression=Attr("status").eq(TaskStatusEnum.CLEAN_UP.value),
        )
        logger.info(f"Found {len(items)} tasks to clean up")
        [self.delete_task(Task.to_cls(item)) for item in items]
        logger.info("Task cleanup completed")

    def __update_task(self, task: Task):
        logger.info(
            f"Updating task status to {task.status.value} for task id: {task.id}"
        )
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
