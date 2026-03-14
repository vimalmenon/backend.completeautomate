from datetime import datetime
from uuid import uuid4

from backend.data import (
    JobData,
)
from backend.database import JobDB
from backend.enum import JobsStatusEnum, JobTypeEnum


class JobManager:

    def save_job(self, job_data: JobData):
        JobDB().save_data(job_data)

    def get_job_by_type(self, type: JobTypeEnum) -> list[JobData]:
        return JobDB().query_data_by_type(type)

    def create_job(
        self,
        type: JobTypeEnum,
        task_data: dict,
        description: str,
        status: JobsStatusEnum = JobsStatusEnum.IN_PROGRESS,
    ) -> JobData:
        return JobData(
            id=uuid4(),
            status=status,
            type=type,
            task_data=task_data,
            description=description,
            created_at=datetime.now(),
        )
