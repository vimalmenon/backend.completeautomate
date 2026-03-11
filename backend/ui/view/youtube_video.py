from nicegui import run, ui

from backend.data import PlatformDBData, PlatformYouTubeVideoDBData
from backend.enum import PlatformEnum
from backend.manager import YouTubeVideoManager
from backend.ui.common.component_common import (
    render_common_header,
    render_separator,
)


async def youtube_video_page(
    channel_id: str, video_id: str, section: str | None = None
):
    platform = PlatformDBData(
        platform_type=PlatformEnum.YouTubeVideo,
        data=PlatformYouTubeVideoDBData(channel_id=channel_id, video_id=video_id),
    )
    render_common_header(page_title="YouTube Videos")
    render_separator()

    # Show loading spinner while fetching tasks
    with ui.row().classes("w-full items-center my-4") as loading_row:
        ui.spinner(size="lg", color="primary")
        ui.label("Loading video...")

        video = await run.io_bound(
            lambda: YouTubeVideoManager(ref_id=platform.ref_id).get_video()
        )

    # Remove loading indicator
    loading_row.delete()

    if not video:
        with ui.row().classes("w-full"):
            ui.label(f"No video found with {video_id}")
        return

    # TODO Show Video Status
    # TODO Edit Video
    # TODO Show VIDEO Details
    # TODO Edit transcript
    if video:
        pass
