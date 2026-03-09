from functools import lru_cache
from typing import TypedDict

from nicegui import ui

from backend.config.env import env
from backend.manager import TaskManager
from backend.ui.service.work_offline import load_initial_data


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


stat_cards = [
    {"label": "All Tasks", "value": "", "icon": "hourglass_empty", "color": "violet"},
    {
        "label": "IN PROGRESS",
        "value": "IN_PROGRESS",
        "icon": "schedule",
        "color": "blue",
    },
    {
        "label": "COMPLETED",
        "value": "COMPLETED",
        "icon": "check_circle",
        "color": "green",
    },
    {
        "label": "IN REVIEW",
        "value": "REVIEW",
        "icon": "hourglass_empty",
        "color": "gray",
    },
    {"label": "FAILED", "value": "FAILED", "icon": "error", "color": "red"},
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
        target = f"/tasks?status={status}" if status else "/tasks"
        ui.run_javascript(f'window.location.href = "{target}"')

    return _handler


def main_page():
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
                    "links_to": f"/channel/{env.YOUTUBE_CHANNEL_ID}",
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

    # Hero Section
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

    with ui.row().classes("items-center"):
        with ui.avatar(color="blue", text_color="white", size="lg"):
            ui.icon("task", size="md")
        with ui.column().classes("gap-0"):
            ui.label("Tasks").classes("text-h6 font-bold")
            ui.label("Manage and schedule automated content creation tasks").classes(
                "text-caption text-gray-600"
            )
    # Quick Stats Section (placeholder for future metrics)
    with ui.row().classes("w-full gap-4 mt-6 flex-wrap"):

        for stat in stat_cards:
            with (
                ui.card()
                .classes(
                    f"flex-1 min-w-[200px] shadow-md hover:shadow-lg transition-shadow border-t-4 border-{stat['color']}-500"
                )
                .on("click", make_tasks_navigation_handler(stat["value"]))
            ):
                with ui.avatar(color=stat["color"], text_color="white", size="md"):
                    ui.icon(stat["icon"], size="md")
                with ui.column().classes("gap-0 "):
                    ui.label(stat["label"]).classes("text-subtitle2 text-gray-600")
                    ui.label(str(get_status_counts(stat["value"]))).classes(
                        "text-h5 font-bold"
                    )
    ui.separator().classes("my-6")
    # Navigation Sections
    ui.label("Navigation").classes("text-h5 font-bold mb-4")

    with ui.grid(columns="1 sm:2 lg:3").classes("w-full gap-4"):
        for section in menu_items:
            with ui.card().classes(
                # f"shadow-md hover:shadow-xl transition-all hover:scale-[1.02] cursor-pointer "
                f"border-t-4 border-{section['color']}-500"
            ):
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
