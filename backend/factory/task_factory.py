from datetime import datetime
from uuid import uuid4

from backend.data import TaskData
from backend.enum import JobEnum, TaskStatusEnum


def create_task_factory(**kwargs) -> TaskData:
    return TaskData(
        id=kwargs.get("id", uuid4()),
        job_type=kwargs.get("job_type", JobEnum.YouTubeChannel),
        payload=kwargs.get("payload", {}),
        created_by=kwargs.get("created_by", "OWNER"),
        created_at=kwargs.get("created_at", datetime.now()),
        status=kwargs.get("status", TaskStatusEnum.NEW),
    )


def create_tasks_factory(items: list[dict] = []) -> list[TaskData]:
    return [create_task_factory(**key) for key in items]
