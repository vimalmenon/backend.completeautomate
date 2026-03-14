from backend.data import JobData
from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.generator import YouTubeChannelCreator


class YouTubeChannelJob:
    types = [JobTypeEnum.YouTubeChannel]

    def __init__(self, job: JobData):
        self.job = job

    def execute(self) -> tuple[JobsStatusEnum, int]:
        if self.job.type == JobTypeEnum.YouTubeChannel:
            status = YouTubeChannelCreator().generate()
            return (status, 0)
        return (JobsStatusEnum.IN_PROGRESS, 0)
