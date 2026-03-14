from backend.data import JobData
from backend.enum import JobsStatusEnum, JobTypeEnum


class YouTubeChannelJob:
    types = [JobTypeEnum.YouTubeChannel]

    def __init__(self, job: JobData):
        self.job = job

    def execute(self) -> tuple[JobsStatusEnum, int]:
        # Implement the logic to execute the YouTube channel job here
        return (JobsStatusEnum.IN_PROGRESS, 0)
