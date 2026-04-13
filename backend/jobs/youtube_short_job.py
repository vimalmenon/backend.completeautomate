from backend.data import JobDataResponse
from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.generator import YouTubeShortGenerator
from backend.jobs.base_job import BaseJob


class YouTubeShortJob(BaseJob):
    types = [JobTypeEnum.YouTubeShortGenerator]

    def execute(self) -> JobDataResponse:
        try:
            if self.job.type == JobTypeEnum.YouTubeShortGenerator:
                status, data = YouTubeShortGenerator().generate()
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
