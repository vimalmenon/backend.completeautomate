from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.generator.youtube import YouTubeVideoGenerator
from backend.jobs.base_job import BaseNewJob


class YouTubeVideoJob(BaseNewJob):
    types = [JobTypeEnum.YouTubeVideo, JobTypeEnum.YouTubeVideoStatsUpdater]

    def execute(self) -> tuple[JobsStatusEnum, int, dict | None]:

        if self.job.type == JobTypeEnum.YouTubeVideo:
            YouTubeVideoGenerator(job=self.job).generate()
            return (JobsStatusEnum.FAILED, 0, None)
        if self.job.type == JobTypeEnum.YouTubeVideoStatsUpdater:
            return (JobsStatusEnum.FAILED, 0, None)
        return (JobsStatusEnum.FAILED, 0, None)
