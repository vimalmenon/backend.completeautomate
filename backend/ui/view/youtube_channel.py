from nicegui import run, ui

from backend.data import PlatformDBData, PlatformYouTubeChannelDBData
from backend.enum import PlatformEnum
from backend.manager import YouTubeChannelManager, YouTubeVideoManager
from backend.ui.common.component_common import render_not_found_message


async def youtube_channel_page(channel_id: str, tab: str | None = None):

    platform = PlatformDBData(
        platform_type=PlatformEnum.YouTubeChannel,
        data=PlatformYouTubeChannelDBData(channel_id=channel_id),
    )
    with ui.row().classes("w-full items-center my-4") as loading_row:
        ui.spinner(size="lg", color="primary")
        ui.label("Loading channel data and videos...")

        channel, videos = await run.io_bound(
            lambda: (
                YouTubeChannelManager(ref_id=platform.ref_id).get_channel_details(),
                YouTubeVideoManager(ref_id=platform.ref_id).get_all_videos(),
            )
        )

    # Remove loading indicator
    loading_row.delete()

    if not channel:
        render_not_found_message(message=f"No Channel found with {channel_id}")
        return

    if not videos:
        render_not_found_message(message=f"No Videos found in the channel {channel_id}")
        return

    for video in videos:
        with ui.row().classes("w-100"):
            ui.label(video.title)
