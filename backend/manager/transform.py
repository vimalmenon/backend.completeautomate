from backend.database import (
    YouTubeChannelDB,
    YouTubeChannelUnmanagedDB,
    YouTubeVideoDB,
    YouTubeVideoUnmanagedDB,
)


def transform_data() -> bool:
    channels = YouTubeChannelUnmanagedDB().get_channels()
    for channel in channels:
        YouTubeChannelDB(channel.ref_id).update_values({"channel_id": channel.platform.channel_id})

    videos = YouTubeVideoUnmanagedDB().get_all_videos_from_db()
    for video in videos:
        YouTubeVideoDB(ref_id=video.ref_id).update_values({"channel_id": video.platform.channel_id, "video_id": video.platform.video_id})
    return False
