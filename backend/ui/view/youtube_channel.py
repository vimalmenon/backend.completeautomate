from nicegui import run, ui

from backend.manager import YouTubeChannelManager, YouTubeVideoManager


async def youtube_channel_page(tab="channel"):

    with ui.row().classes("w-full items-center my-4") as loading_row:
        ui.spinner(size="lg", color="primary")
        ui.label("Loading tasks...")

        await run.io_bound(
            YouTubeVideoManager().get_all_videos(channel_id=""),
            YouTubeChannelManager(channel_id="").get_channel_details(),
        )

    # Remove loading indicator
    loading_row.delete()
