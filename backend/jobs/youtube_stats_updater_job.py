from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.jobs.base_job import BaseJob


class YouTubeStatsUpdaterJob(BaseJob):
    types = [JobTypeEnum.YouTubeStatsUpdater]

    def execute(self) -> tuple[JobsStatusEnum, int, dict | None]:
        return (JobsStatusEnum.IN_PROGRESS, 0, None)
