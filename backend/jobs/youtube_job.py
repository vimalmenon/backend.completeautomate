from backend.enum import JobsStatusEnum
from backend.jobs.base_job import BaseJob


class YouTubeJob(BaseJob):
    def execute(self) -> tuple[JobsStatusEnum, int, dict | None]:
        return (JobsStatusEnum.IN_PROGRESS, 0, None)
