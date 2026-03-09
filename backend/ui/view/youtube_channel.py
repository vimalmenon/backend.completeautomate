from nicegui import run, ui

from backend.manager import YouTubeChannelManager, YouTubeVideoManager


async def youtube_channel_page(tab="channel"):

    with ui.row().classes("w-full items-center my-4") as loading_row:
        ui.spinner(size="lg", color="primary")
        ui.label("Loading tasks...")

        channel, videos = await run.io_bound(
            lambda: (
                YouTubeChannelManager(channel_id="").get_channel_details(),
                YouTubeVideoManager().get_all_videos(channel_id=""),
            )
        )

    # Remove loading indicator
    loading_row.delete()
