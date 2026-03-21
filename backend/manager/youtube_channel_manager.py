from backend.data import YouTubeChannelDBData
from backend.database import YouTubeChannelDB


class YouTubeChannelManager:
    def __init__(self, ref_id: str):
        self.channel_db = YouTubeChannelDB(ref_id=ref_id)

    def add_channel(self, data: YouTubeChannelDBData) -> None:
        return self.channel_db.add_channel(data)

    def get_channel_details(self) -> YouTubeChannelDBData | None:
        return self.channel_db.query_channel()

    def save_data(self, data: YouTubeChannelDBData) -> None:
        return self.channel_db.add_channel(data)

    def update_channel(self, value: dict):
        self.channel_db.update_channel(value)

    def get_channels(self) -> list[YouTubeChannelDBData]:
        return self.channel_db.get_channels()
