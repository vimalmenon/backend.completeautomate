from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.jobs.base_job import BaseNewJob


class YouTubeVideoJob(BaseNewJob):
    types = [JobTypeEnum.YouTubeVideo, JobTypeEnum.YouTubeVideoStatsUpdater]

    def execute(self) -> tuple[JobsStatusEnum, int, dict | None]:

        if self.job.type == JobTypeEnum.YouTubeVideo:
            pass
        if self.job.type == JobTypeEnum.YouTubeVideoStatsUpdater:
            pass
        return (JobsStatusEnum.FAILED, 0, None)
