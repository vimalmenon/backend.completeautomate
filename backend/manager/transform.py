from backend.database import YouTubeChannelDB


def transform_data() -> bool:
    channels = YouTubeChannelDB().get_channels()
    for channel in channels:
        YouTubeChannelDB(channel.ref_id).update_values({"channel_id": channel.platform.channel_id})
    return False
