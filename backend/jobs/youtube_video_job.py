from backend.enum import JobsStatusEnum, JobTypeEnum


class YouTubeVideoJob:
    types = [JobTypeEnum.YouTubeVideo, JobTypeEnum.YouTubeVideoStatsUpdater]

    def execute(self) -> tuple[JobsStatusEnum, int]:
        return (JobsStatusEnum.IN_PROGRESS, 0)
