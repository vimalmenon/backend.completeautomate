from backend.config.env import env
from backend.enum import YouTubeVideoTaskEnum
from backend.manager.platform_manager import PlatformManager
from backend.manager.youtube_video_manager import YouTubeVideoManager


class OneTimeScript:
    def __init__(self):
        self.platform_db = PlatformManager()
        self.ref_id = self.platform_db.get_platform_by_channel_id(
            channel_id=env.YOUTUBE_CHANNEL_ID
        )
        self.video_db = YouTubeVideoManager(ref_id=self.ref_id)

    def start(self) -> bool:
        # Need to add when there is some transform data
        videos = self.video_db.get_all_videos()
        for video in videos:
            video.status = YouTubeVideoTaskEnum.YouTubeVideoStart
            video.channel_id = env.YOUTUBE_CHANNEL_ID
            # TODO Need to implement this
        return False
