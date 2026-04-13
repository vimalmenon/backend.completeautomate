from backend.data import JobDataResponse
from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.generator import YouTubeShortGenerator
from backend.jobs.base_job import BaseJob


class YouTubeShortJob(BaseJob):
    types = [JobTypeEnum.YouTubeShortGenerator]

    def execute(self) -> JobDataResponse:
        if self.job.type == JobTypeEnum.YouTubeShortGenerator:
            status, data = YouTubeShortGenerator().generate()
            return JobDataResponse(status=status, task_data=data)
        return JobDataResponse(status=JobsStatusEnum.IN_PROGRESS)
