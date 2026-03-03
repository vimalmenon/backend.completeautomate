from datetime import datetime
from uuid import uuid4

from backend.data import TaskData
from backend.enum import JobEnum, TaskStatusEnum, TeamEnum


def create_task(payload=dict) -> TaskData:
    return TaskData(
        id=uuid4(),
        job_type=JobEnum.YouTubeChannel,
        payload=payload,
        created_by=TeamEnum.OWNER,
        created_at=datetime.now(),
        status=TaskStatusEnum.NEW,
    )


def create_tasks(int_number=5) -> list[TaskData]:
    return [create_task() for _i in (0, int_number)]
