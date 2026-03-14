from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.jobs.base_job import BaseNewJob


class YouTubeVideoJob(BaseNewJob):
    types = [JobTypeEnum.YouTubeVideo, JobTypeEnum.YouTubeVideoStatsUpdater]

    def execute(self) -> tuple[JobsStatusEnum, int, dict | None]:
        return (JobsStatusEnum.IN_PROGRESS, 0, None)
