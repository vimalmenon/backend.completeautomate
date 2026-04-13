from backend.manager.youtube_channel_manager import YouTubeChannelManager


def transform_data() -> bool:
    channels = YouTubeChannelManager(ref_id="").get_channels()
    for channel in channels:
        YouTubeChannelManager(ref_id=channel.ref_id).update_channel({"playlist": []})

    return False
