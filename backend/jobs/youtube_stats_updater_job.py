from backend.data import YouTubeChannelDBData, YouTubeVideoDBData
from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.integration import YouTubeAPI
from backend.jobs.base_job import BaseJob
from backend.manager import YouTubeChannelManager, YouTubeVideoManager


class YouTubeStatsUpdaterJob(BaseJob):
    types = [JobTypeEnum.YouTubeStatsUpdater]
    UPDATE_DAYS = 2

    def __init__(self, job):
        super().__init__(job)
        self.channel_manager = YouTubeChannelManager(ref_id="")
        self.video_manager = YouTubeVideoManager(ref_id="")
        self.youtube_api = YouTubeAPI()

    def execute(self) -> tuple[JobsStatusEnum, int, dict | None]:
        channels = self.channel_manager.get_channels()
        for channel in channels:
            self.__process_channel(channel=channel)
            self.__process_videos_for_channel(channel=channel)
        return (JobsStatusEnum.IN_PROGRESS, 0, None)

    def __process_channel(self, channel: YouTubeChannelDBData) -> None:
        if channel.past_update_time(days=self.UPDATE_DAYS):
            channel_data = self.youtube_api.get_channel_info(
                channel_id=channel.platform.channel_id
            )
            channel_db = YouTubeChannelDBData.to_cls_from_response(channel=channel_data)
            self.channel_manager.update_channel(
                value=channel_db.values_to_update(old_value=channel)
            )

    def __process_videos_for_channel(self, channel: YouTubeChannelDBData):
        videos = self.video_manager.get_videos_by_channel(
            channel_id=channel.platform.channel_id
        )
        for video in videos:
            self.__process_video(video=video)

    def __process_video(self, video: YouTubeVideoDBData) -> None:
        if video.past_update_time(days=self.UPDATE_DAYS):
            video_api = self.youtube_api.fetch_video_details(
                video_id=video.platform.video_id
            )
            video_db = YouTubeVideoDBData.to_cls_from_response(item=video_api)
            self.video_manager.update_video(
                values=video_db.values_to_update(old_value=video)
            )
