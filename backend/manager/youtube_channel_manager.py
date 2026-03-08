from backend.data import YouTubeChannelDBData
from backend.database import YouTubeChannelDB


class YouTubeChannelManager:
    def __init__(self, channel_id: str):
        self.channel_id = channel_id

    def get_channel_details(self) -> YouTubeChannelDBData | None:
        return YouTubeChannelDB(channel_id=self.channel_id).query_channel()
