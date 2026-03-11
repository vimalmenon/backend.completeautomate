from nicegui import run, ui

from backend.manager import YouTubeChannelManager, YouTubeVideoManager


async def youtube_channel_page(channel_id: str, tab: str | None = None):

    with ui.row().classes("w-full items-center my-4") as loading_row:
        ui.spinner(size="lg", color="primary")
        ui.label("Loading channel data and videos...")

        channel, videos = await run.io_bound(
            lambda: (
                YouTubeChannelManager(channel_id).get_channel_details(),
                YouTubeVideoManager(channel_id).get_all_videos(),
            )
        )

    # Remove loading indicator
    loading_row.delete()
