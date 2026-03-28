from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.generator import YouTubeVideoGenerator
from backend.jobs.base_job import BaseJob


class YouTubeVideoJob(BaseJob):
    types = [JobTypeEnum.YouTubeVideo]

    def execute(self) -> tuple[JobsStatusEnum, int, dict | None]:

        if self.job.type == JobTypeEnum.YouTubeVideo:
            job_status, task_data = YouTubeVideoGenerator(job=self.job).generate()
            return (job_status, 0, task_data)
        return (JobsStatusEnum.FAILED, 0, None)
