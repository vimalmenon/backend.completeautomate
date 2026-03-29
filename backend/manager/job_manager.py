from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from backend.data import (
    JobData,
)
from backend.database import JobDB
from backend.enum import JobsStatusEnum, JobTypeEnum


class JobManager:

    def save_job(self, job_data: JobData) -> None:
        JobDB().save_data(job_data)

    def delete_job(self, job_data: JobData) -> None:
        JobDB().delete_data(job_id=str(job_data.id))

    def get_job_by_type(self, type: JobTypeEnum) -> list[JobData]:
        return JobDB().query_data_by_type(type)

    def get_job_by_ref_id(self, ref_id: str):
        pass

    def get_job_by_id(self, job_id: str) -> JobData | None:
        return JobDB().get_job_by_id(job_id)

    def get_all_jobs(self) -> list[JobData]:
        return JobDB().get_all_jobs()

    def get_all_active_jobs(self) -> list[JobData]:
        return JobDB().get_all_active_jobs()

    def get_all_offline_jobs(self) -> list[JobData]:
        return JobDB().get_jobs_by_statuses(
            statuses=[
                JobsStatusEnum.IN_PROGRESS,
                JobsStatusEnum.FAILED,
                JobsStatusEnum.REVIEW,
            ]
        )

    def get_all_completed_job(self) -> list[JobData]:
        return JobDB().get_jobs_by_status(status=JobsStatusEnum.COMPLETE)

    def get_all_cleanup_job(self) -> list[JobData]:
        return JobDB().get_jobs_by_status(status=JobsStatusEnum.CLEAN_UP)

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

    def update_job_data(
        self,
        job_id: UUID,
        status: JobsStatusEnum,
        failed_count: int,
        task_data: dict | None = None,
    ) -> None:
        values: dict[str, Any] = {
            "status": status.value,
            "failed_count": failed_count,
        }
        if task_data:
            values["task_data"] = task_data

        JobDB().update_data(
            job_id=job_id,
            values=values,
        )

    def update_job_status(
        self,
        job_id: UUID,
        status: JobsStatusEnum,
    ):
        values: dict[str, Any] = {
            "status": status.value,
        }
        JobDB().update_data(
            job_id=job_id,
            values=values,
        )

    def create_youtube_channel_onboarding_job(self) -> JobData:
        if jobs := self.get_job_by_type(type=JobTypeEnum.YouTubeChannelOnboarding):
            return jobs[0]
        job_data = self.create_job(
            type=JobTypeEnum.YouTubeChannelOnboarding,
            task_data={},
            description="Onboard YouTube Channels",
        )
        self.save_job(job_data=job_data)
        return job_data
