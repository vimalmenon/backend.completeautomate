from uuid import uuid4

from backend.data import TaskData
from backend.enum import JobEnum, TaskStatusEnum
from backend.factory.common import faker


def create_task_factory(**kwargs) -> TaskData:
    return TaskData(
        id=kwargs.get("id", uuid4()),
        job_type=kwargs.get("job_type", JobEnum.YouTubeChannel),
        payload=kwargs.get("payload", {}),
        created_by=kwargs.get("created_by", "OWNER"),
        created_at=kwargs.get("created_at", faker.date_time()),
        status=kwargs.get("status", TaskStatusEnum.NEW),
    )


def create_video_task_factor(**kwargs) -> TaskData:
    return TaskData(
        id=kwargs.get("id", uuid4()),
        job_type=JobEnum.YouTubeVideo,
        status=kwargs.get("status", TaskStatusEnum.NEW),
        payload=kwargs.get("payload", {}),
        created_by=kwargs.get("created_by", "OWNER"),
        created_at=kwargs.get("created_at", faker.date_time()),
    )


def create_channel_task_factory(**kwargs) -> TaskData:
    return TaskData(
        id=kwargs.get("id", uuid4()),
        job_type=JobEnum.YouTubeChannel,
        payload=kwargs.get("payload", {}),
        status=kwargs.get("status", TaskStatusEnum.NEW),
        created_by=kwargs.get("created_by", "OWNER"),
        created_at=kwargs.get("created_at", faker.date_time()),
    )


def create_tasks_factory(items: list[dict] = []) -> list[TaskData]:
    return [create_task_factory(**key) for key in items]
