import logging

from nicegui import ui

from backend.config.env import env
from backend.config.logging_config import setup_logging
from backend.ui import (  # tasks_page,
    channel_detail_page,
    main_page,
    prompt_detail_page,
    prompt_page,
    s3_bucket_page,
    task_detail_page,
    video_detail_page,
    youtube_page,
)
from backend.ui.service.work_offline import toggle_offline_mode
from backend.ui.view import tasks_page, youtube_video_page

logger = logging.getLogger(__name__)


def root():

    # Dark mode toggle
    dark = ui.dark_mode()
    ui.page_title("CompleteAutomate Dashboard")

    # Navigation header with page change feedback
    with ui.header().classes("items-center justify-between shadow-lg"):
        with ui.row().classes("items-center"):
            ui.icon("dashboard", size="md").classes("mr-2")
            ui.label("CompleteAutomate").classes("text-h5 font-bold")

        with ui.row().classes("gap-4 items-center"):
            # Navigation buttons with icons
            with ui.button(
                icon="home",
                on_click=lambda: ui.run_javascript('window.location.href = "/"'),
            ).props("flat"):
                ui.tooltip("Home")
            with ui.button(
                icon="task",
                on_click=lambda: ui.run_javascript('window.location.href = "/tasks"'),
            ).props("flat"):
                ui.tooltip("Tasks")
            with ui.button(
                icon="video_library",
                on_click=lambda: ui.run_javascript('window.location.href = "/youtube"'),
            ).props("flat"):
                ui.tooltip("YouTube")
            with ui.button(
                icon="article",
                on_click=lambda: ui.run_javascript('window.location.href = "/prompt"'),
            ).props("flat"):
                ui.tooltip("Prompts")
            with ui.button(
                icon="cloud",
                on_click=lambda: ui.run_javascript('window.location.href = "/s3"'),
            ).props("flat"):
                ui.tooltip("S3 Bucket")

            ui.separator().props("vertical")
            ui.switch(
                "Offline",
                value=env.OFFLINE,
                on_change=lambda e: toggle_offline_mode(bool(e.value)),
            ).props("dense")
            ui.switch("Dark").bind_value(dark).props("dense")

    # Progress bar for page loading
    progress = ui.linear_progress(value=0).classes("w-full")
    progress.visible = False

    # Main content area with smooth transitions
    with ui.element("div").classes("w-full transition-all duration-300"):
        ui.sub_pages(
            {
                "/": main_page,
                "/tasks": tasks_page,
                "/task/{task_id}": task_detail_page,
                "/youtube": youtube_page,
                "/youtube/{channel_id}/{video_id}": youtube_video_page,
                "/video/{ref_id}": video_detail_page,
                "/channel/{channel_id}": channel_detail_page,
                "/prompt": prompt_page,
                "/prompt/{task_id}": prompt_detail_page,
                "/s3": s3_bucket_page,
            }
        ).classes("w-full p-4")

    # Add page change notification
    ui.add_head_html("""
        <style>
            .page-transition {
                animation: fadeIn 0.3s ease-in;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
    """)


def main() -> None:
    # Initialize logging
    setup_logging(log_dir="logs")
    logger.info("Starting CompleteAutomate GUI")
    ui.run(
        root,
        title="CompleteAutomate",
        favicon="🤖",
        storage_secret="completeautomate-secret-key",  # Required for app.storage.user
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
