from nicegui import run, ui

from backend.manager import YouTubeVideoManager
from backend.ui.common.component_common import (
    render_common_header,
    render_separator,
)


async def youtube_videos_page(
    channel_id: str, video_id: str, section: str | None = None
):
    render_common_header(page_title="YouTube Videos")
    render_separator()

    # Show loading spinner while fetching tasks
    with ui.row().classes("w-full items-center my-4") as loading_row:
        ui.spinner(size="lg", color="primary")
        ui.label("Loading tasks...")

        video = await run.io_bound(
            lambda: YouTubeVideoManager().get_video_by_id(channel_id, video_id)
        )

    # Remove loading indicator
    loading_row.delete()

    if not video:
        pass
