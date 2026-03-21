from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.generator import YouTubeVideoGenerator, YouTubeVideoStatsUpdate
from backend.jobs.base_job import BaseJob


class YouTubeVideoJob(BaseJob):
    types = [JobTypeEnum.YouTubeVideo, JobTypeEnum.YouTubeVideoStatsUpdater]

    def execute(self) -> tuple[JobsStatusEnum, int, dict | None]:

        if self.job.type == JobTypeEnum.YouTubeVideo:
            job_status, task_data = YouTubeVideoGenerator(job=self.job).generate()
            return (job_status, 0, task_data)
        if self.job.type == JobTypeEnum.YouTubeVideoStatsUpdater:
            YouTubeVideoStatsUpdate()
            return (JobsStatusEnum.IN_PROGRESS, 0, None)
        return (JobsStatusEnum.FAILED, 0, None)
