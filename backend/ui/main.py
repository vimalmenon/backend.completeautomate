from functools import lru_cache
from typing import TypedDict

from nicegui import ui

from backend.config.env import env
from backend.data import PlatformDBData, PlatformYouTubeChannelDBData
from backend.enum import PlatformEnum, TaskStatusEnum
from backend.manager import TaskManager, YouTubeChannelManager, YouTubeVideoManager
from backend.ui.service.work_offline import load_initial_data

channels = [env.YOUTUBE_CHANNEL_ID]


class MenuItem(TypedDict):
    name: str
    icon: str
    links_to: str
    description: str


class MenuSection(TypedDict):
    category: str
    icon: str
    description: str
    color: str
    items: list[MenuItem]


tasks_cards = [
    {"label": "All Tasks", "value": "", "icon": "hourglass_empty", "color": "violet"},
    {
        "label": "IN PROGRESS",
        "value": TaskStatusEnum.IN_PROGRESS.value,
        "icon": "schedule",
        "color": "blue",
    },
    {
        "label": "COMPLETED",
        "value": TaskStatusEnum.COMPLETED.value,
        "icon": "check_circle",
        "color": "green",
    },
    {
        "label": "IN REVIEW",
        "value": TaskStatusEnum.REVIEW.value,
        "icon": "hourglass_empty",
        "color": "gray",
    },
    {
        "label": "FAILED",
        "value": TaskStatusEnum.FAILED.value,
        "icon": "error",
        "color": "red",
    },
]


def get_status_counts(status: str) -> int:
    tasks = get_cached_tasks()
    if status == "":
        return len(tasks)
    return sum(1 for task in tasks if task.status == status)


@lru_cache(maxsize=1)
def get_cached_tasks():
    return tuple(TaskManager().get_tasks())


def make_tasks_navigation_handler(status: str):
    def _handler() -> None:
        target = f"/jobs?status={status}" if status else "/jobs"
        ui.run_javascript(f'window.location.href = "{target}"')

    return _handler


def _render_hero_section() -> None:
    """Render the dashboard hero section."""
    with ui.card().classes(
        "w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg"
    ):
        with ui.column().classes("gap-2 py-8 px-4"):
            ui.icon("auto_awesome", size="xl").classes("mb-2")
            ui.label("CompleteAutomate Dashboard").classes("text-h3 font-bold")
            ui.label("Your AI-Powered Content Automation Platform").classes(
                "text-h6 opacity-90"
            )
    ui.separator().classes("my-6")


def _render_tasks_header() -> None:
    """Render the tasks section header."""
    with ui.row().classes("items-center"):
        with ui.avatar(color="blue", text_color="white", size="lg"):
            ui.icon("task", size="md")
        with ui.column().classes("gap-0"):
            ui.label("Tasks").classes("text-h6 font-bold")
            ui.label("Manage and schedule automated content creation tasks").classes(
                "text-caption text-gray-600"
            )


def _render_tasks_stats_cards() -> None:
    """Render task status cards."""
    with ui.row().classes("w-full gap-4 mt-6 flex-wrap"):
        for task in tasks_cards:
            with (
                ui.card()
                .classes(
                    f"flex-1 min-w-[200px] shadow-md hover:shadow-lg transition-shadow border-t-4 border-{task['color']}-500"
                )
                .on("click", make_tasks_navigation_handler(task["value"]))
            ):
                with ui.avatar(color=task["color"], text_color="white", size="md"):
                    ui.icon(task["icon"], size="md")
                with ui.column().classes("gap-0 "):
                    ui.label(task["label"]).classes("text-subtitle2 text-gray-600")
                    ui.label(str(get_status_counts(task["value"]))).classes(
                        "text-h5 font-bold"
                    )


def _format_count(count) -> str:
    """Format a count value as string with commas."""
    if isinstance(count, str):
        return count
    return f"{int(count):,}" if count > 0 else "0"


def _render_channel_stats(channel_detail, channel_videos) -> None:
    """Render channel statistics."""
    ui.separator().classes("my-4")
    with ui.row().classes("w-full gap-4 justify-between"):
        # Videos
        with ui.column().classes("gap-1 items-center flex-1"):
            ui.label("Videos").classes(
                "text-xs font-semibold text-gray-600 dark:text-gray-400"
            )
            ui.label(str(len(channel_videos))).classes(
                "text-h5 font-bold text-blue-600 dark:text-blue-400"
            )

        # Subscribers
        if (
            hasattr(channel_detail, "subscriber_count")
            and channel_detail.subscriber_count
        ):
            with ui.column().classes("gap-1 items-center flex-1"):
                ui.label("Subscribers").classes(
                    "text-xs font-semibold text-gray-600 dark:text-gray-400"
                )
                ui.label(_format_count(channel_detail.subscriber_count)).classes(
                    "text-h5 font-bold text-green-600 dark:text-green-400"
                )

        # Total Views
        if hasattr(channel_detail, "view_count") and channel_detail.view_count:
            with ui.column().classes("gap-1 items-center flex-1"):
                ui.label("Total Views").classes(
                    "text-xs font-semibold text-gray-600 dark:text-gray-400"
                )
                ui.label(_format_count(channel_detail.view_count)).classes(
                    "text-h5 font-bold text-purple-600 dark:text-purple-400"
                )


def _render_channel_card(channel: str, channel_detail, channel_videos) -> None:
    """Render a single channel card."""
    with ui.card().classes("w-full border-t-4 border-red-500"):
        # Top section: Image and basic info
        with ui.row().classes("gap-6 items-start w-full"):
            # Channel thumbnail
            ui.image(channel_detail.thumbnail_url).classes(
                "w-32 h-32 rounded-full flex-shrink-0 object-cover"
            )

            # Channel info section
            with ui.column().classes("flex-1 gap-2"):
                # Channel name
                ui.label(channel_detail.title).classes(
                    "text-h6 font-bold text-gray-900 dark:text-white"
                )

                # Channel URL
                if hasattr(channel_detail, "custom_url") and channel_detail.custom_url:
                    with ui.row().classes("items-center gap-2"):
                        ui.label("URL:").classes(
                            "font-semibold text-sm text-gray-700 dark:text-gray-300"
                        )
                        ui.label(channel_detail.custom_url).classes(
                            "text-sm text-blue-600 dark:text-blue-400 break-all"
                        )

                # Description
                if channel_detail.description:
                    ui.label(channel_detail.description).classes(
                        "text-sm text-gray-600 dark:text-gray-400 text-wrap mt-2"
                    )

        # Statistics section
        _render_channel_stats(channel_detail, channel_videos)

        # Navigation button
        ui.separator().classes("my-4")
        with ui.row().classes("w-full justify-end"):
            ui.button(
                "View Channel Details",
                icon="arrow_forward",
                on_click=lambda target=channel: ui.run_javascript(
                    f'window.location.href = "/youtube/{target}"'
                ),
            ).props("color=red")


def _render_youtube_channels_section() -> None:
    """Render YouTube channels section."""
    ui.label("YouTube Channels").classes("text-h5 font-bold")
    for channel in channels:
        platform = PlatformDBData(
            platform_type=PlatformEnum.YouTubeChannel,
            data=PlatformYouTubeChannelDBData(channel_id=channel),
        )
        channel_detail = YouTubeChannelManager(
            ref_id=platform.ref_id
        ).get_channel_details()
        channel_videos = YouTubeVideoManager(ref_id=platform.ref_id).get_all_videos()
        if not channel_detail:
            with ui.row().classes("w-full gap-4 items-center"):
                ui.icon("error", color="red").classes("text-xl")
                ui.label(f"Channel ID {channel} not found").classes(
                    "text-subtitle2 text-gray-600"
                )
        else:
            _render_channel_card(channel, channel_detail, channel_videos)


def _render_navigation_section(menu_items: list[MenuSection]) -> None:
    """Render the navigation menu section."""
    ui.label("Navigation").classes("text-h5 font-bold mb-4")
    with ui.grid(columns="1 sm:2 lg:3").classes("w-full gap-4"):
        for section in menu_items:
            with ui.card().classes(f"border-t-4 border-{section['color']}-500"):
                with ui.column().classes("gap-3 p-2"):
                    # Section Header
                    with ui.row().classes("items-center gap-3 mb-2"):
                        with ui.avatar(
                            color=section["color"], text_color="white", size="lg"
                        ):
                            ui.icon(section["icon"], size="md")
                        with ui.column().classes("gap-0"):
                            ui.label(section["category"]).classes("text-h6 font-bold")
                            ui.label(section["description"]).classes(
                                "text-caption text-gray-600"
                            )

                    ui.separator()

                    # Section Items
                    with ui.column().classes("gap-2 w-full"):
                        for item in section["items"]:
                            with (
                                ui.button(
                                    icon=item["icon"],
                                    on_click=lambda target=item[
                                        "links_to"
                                    ]: ui.run_javascript(
                                        f'window.location.href = "{target}"'
                                    ),
                                )
                                .props("flat color=primary align=left")
                                .classes("w-full justify-start")
                            ):
                                with ui.row().classes("items-center gap-2 w-full"):
                                    with ui.column().classes("gap-0 flex-1"):
                                        ui.label(item["name"]).classes("font-semibold")
                                        ui.label(item["description"]).classes(
                                            "text-caption text-gray-500"
                                        )
                                    ui.icon("chevron_right").classes("text-gray-400")


def main_page():
    """Render the main dashboard page."""
    # Load initial data for offline mode
    load_initial_data()

    # Refresh cache per page render, then reuse cached tasks for all stat cards.
    get_cached_tasks.cache_clear()

    menu_items: list[MenuSection] = [
        {
            "category": "YouTube",
            "icon": "video_library",
            "description": "Manage YouTube videos, channels, and metadata",
            "color": "red",
            "items": [
                {
                    "name": "List Videos",
                    "icon": "ondemand_video",
                    "links_to": "/youtube",
                    "description": "View and manage YouTube videos",
                },
                {
                    "name": "List Channel",
                    "icon": "live_tv",
                    "links_to": f"/youtube/{env.YOUTUBE_CHANNEL_ID}",
                    "description": "View channel details and statistics",
                },
            ],
        },
        {
            "category": "Prompt",
            "icon": "article",
            "description": "View and manage AI prompts for content generation",
            "color": "green",
            "items": [
                {
                    "name": "List Prompts",
                    "icon": "description",
                    "links_to": "/prompt",
                    "description": "Browse all AI prompts",
                },
            ],
        },
        {
            "category": "Storage",
            "icon": "cloud",
            "description": "Browse objects currently stored in the S3 bucket",
            "color": "orange",
            "items": [
                {
                    "name": "S3 Bucket Items",
                    "icon": "folder_open",
                    "links_to": "/s3",
                    "description": "List and inspect bucket object paths",
                },
            ],
        },
    ]

    # Render page sections
    _render_hero_section()
    _render_tasks_header()
    _render_tasks_stats_cards()
    ui.separator().classes("my-6")
    _render_youtube_channels_section()
    _render_navigation_section(menu_items)
