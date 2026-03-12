from nicegui import run, ui

from backend.data import PlatformDBData, PlatformYouTubeVideoDBData
from backend.enum import PlatformEnum
from backend.manager import TaskManager, YouTubeVideoManager
from backend.ui.common.component_common import (
    render_common_header,
    render_separator,
)

steps = [
    "YouTubeVideoCreate",
    "YouTubeSummarize",
    "YoutubeMetadataGenerator",
    "YouTubeMetadataUpdater",
    "YouTubeThumbnailGenerator",
    "YouTubeThumbnailUpdater",
]


def render_task_progress(tasks):
    # TODO Show video status Progress
    pass


def _render_stat_card(icon: str, label: str, value: str) -> None:
    with ui.card().classes("flex-1 min-w-32 p-4 text-center"):
        ui.icon(icon).classes("text-3xl text-primary")
        ui.label(value).classes("text-2xl font-bold mt-1")
        ui.label(label).classes("text-sm text-gray-500")


def _render_video_details(video) -> None:
    # Latest stats (last entry has the most recent data)
    latest_stats = video.stats[-1] if video.stats else None

    with ui.row().classes("w-full gap-4 flex-wrap"):
        # Left column: thumbnail
        with ui.column().classes("shrink-0"):
            if video.thumbnail:
                ui.image(video.thumbnail).classes("w-64 rounded shadow")

        # Right column: title + metadata
        with ui.column().classes("flex-1 gap-2"):
            ui.label(video.title).classes("text-h5 font-bold")

            with ui.row().classes("gap-4 flex-wrap text-sm text-gray-500"):
                ui.label(f"Published: {video.published_at.strftime('%Y-%m-%d')}")
                ui.label(f"Language: {video.language}")
                if video.tags:
                    ui.label(f"Tags: {', '.join(video.tags[:6])}")

    ui.separator().classes("my-4")

    # Stats row
    if latest_stats:
        with ui.row().classes("w-full gap-4 flex-wrap"):
            _render_stat_card("visibility", "Views", f"{latest_stats.views:,}")
            _render_stat_card("thumb_up", "Likes", f"{latest_stats.likes:,}")
            _render_stat_card("comment", "Comments", f"{latest_stats.comments:,}")
            _render_stat_card(
                "update",
                "Stats Updated",
                latest_stats.timestamp.strftime("%Y-%m-%d"),
            )

    # Description
    if video.description:
        ui.separator().classes("my-4")
        ui.label("Description").classes("text-h6 font-bold")
        with ui.card().classes("w-full"):
            ui.label(video.description).classes("text-sm whitespace-pre-wrap")


async def youtube_video_page(
    channel_id: str, video_id: str, section: str | None = None
):
    platform = PlatformDBData(
        platform_type=PlatformEnum.YouTubeVideo,
        data=PlatformYouTubeVideoDBData(channel_id=channel_id, video_id=video_id),
    )
    render_common_header(page_title=f"YouTube Video: {video_id}")
    render_separator()

    # Navigation breadcrumb
    with ui.row().classes("w-full items-center gap-2 mb-2"):
        ui.button(icon="home", on_click=lambda: ui.navigate.to("/")).props("flat dense")
        ui.button(
            icon="arrow_back",
            on_click=lambda: ui.navigate.to(f"/youtube/{channel_id}"),
        ).props("flat dense")
        ui.label(video_id).classes("text-sm text-gray-500")

    # Show loading spinner while fetching
    with ui.row().classes("w-full items-center my-4") as loading_row:
        ui.spinner(size="lg", color="primary")
        ui.label("Loading video...")

        video, tasks = await run.io_bound(
            lambda: (
                YouTubeVideoManager(ref_id=platform.ref_id).get_video(),
                TaskManager().get_task_by_ref_id(ref_id=platform.ref_id),
            )
        )

    # Remove loading indicator
    loading_row.delete()

    if not video:
        with ui.row().classes("w-full"):
            ui.label(f"No video found with {video_id}")
        return

    render_task_progress(tasks)
    _render_video_details(video)
