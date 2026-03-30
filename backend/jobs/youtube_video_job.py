from backend.data import JobDataResponse
from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.generator import YouTubeVideoGenerator
from backend.jobs.base_job import BaseJob


class YouTubeVideoJob(BaseJob):
    types = [JobTypeEnum.YouTubeVideo]

    def execute(self) -> JobDataResponse:

        if self.job.type == JobTypeEnum.YouTubeVideo:
            job_status, task_data = YouTubeVideoGenerator(job=self.job).generate()
            return JobDataResponse(status=job_status, task_data=task_data)
        return JobDataResponse(status=JobsStatusEnum.FAILED)
