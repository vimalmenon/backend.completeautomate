from backend.data import JobDataResponse
from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.jobs.base_job import BaseJob


class YouTubeShortJob(BaseJob):
    types = [JobTypeEnum.YouTubeShortGenerator]

    def execute(self) -> JobDataResponse:
        return JobDataResponse(status=JobsStatusEnum.IN_PROGRESS)
