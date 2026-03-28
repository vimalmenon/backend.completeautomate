from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.generator import YouTubeStatsUpdater
from backend.integration import YouTubeAPI
from backend.jobs.base_job import BaseJob
from backend.manager import YouTubeChannelManager, YouTubeVideoManager


class YouTubeStatsUpdaterJob(BaseJob):
    types = [JobTypeEnum.YouTubeStatsUpdater]

    def __init__(self, job):
        super().__init__(job)
        self.channel_manager = YouTubeChannelManager(ref_id="")
        self.video_manager = YouTubeVideoManager(ref_id="")
        self.youtube_api = YouTubeAPI()

    def execute(self) -> tuple[JobsStatusEnum, int, dict | None]:
        try:
            status, data = YouTubeStatsUpdater(self.job).generate()
            return (status, 0, data)
        except Exception:
            self.job.failed_count += 1
            status = (
                JobsStatusEnum.FAILED
                if self.job.failed_count >= 4
                else JobsStatusEnum.IN_PROGRESS
            )
            return (status, 1, None)
