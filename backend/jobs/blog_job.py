"""Blog job dispatcher — maps BlogGeneration job type to BlogGenerator."""

from backend.data import JobDataResponse
from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.generator import BlogGenerator
from backend.jobs.base_job import BaseJob


class BlogJob(BaseJob):
    types = [JobTypeEnum.BlogGeneration]

    def execute(self) -> JobDataResponse:
        try:
            if self.job.type == JobTypeEnum.BlogGeneration:
                status, data = BlogGenerator(job=self.job).generate()
                return JobDataResponse(status=status, task_data=data)
            return JobDataResponse(status=JobsStatusEnum.IN_PROGRESS)
        except Exception:
            self.job.failed_count += 1
            status = (
                JobsStatusEnum.FAILED
                if self.job.failed_count >= 4
                else JobsStatusEnum.IN_PROGRESS
            )
            return JobDataResponse(status=status, failed_count=self.job.failed_count)
