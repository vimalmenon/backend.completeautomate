import logging

from nicegui import ui

from backend.config.env import env
from backend.config.logging_config import setup_logging
from backend.ui import (
    jobs_page,
    main_page,
    prompt_detail_page,
    prompt_page,
    s3_bucket_page,
    youtube_channel_page,
    youtube_video_page,
)
from backend.ui.service.work_offline import load_initial_data, toggle_offline_mode

logger = logging.getLogger(__name__)


def root():

    # Load initial data based on offline mode
    load_initial_data(env.OFFLINE)

    # Dark mode toggle
    dark = ui.dark_mode()
    ui.page_title("CompleteAutomate Dashboard")

    # Header
    with ui.header().classes("items-center justify-between shadow-lg"):
        with ui.row().classes("items-center"):
            ui.label("CompleteAutomate").classes("text-h5 font-bold")

        with ui.row().classes("gap-4 items-center"):
            ui.switch(
                "Offline",
                value=env.OFFLINE,
                on_change=lambda e: toggle_offline_mode(bool(e.value)),
            ).props("dense")
            ui.switch("Dark").bind_value(dark).props("dense")

    # Main content area with smooth transitions
    with ui.element("div").classes("w-full transition-all duration-300"):
        ui.sub_pages(
            {
                "/": main_page,
                "/jobs": jobs_page,
                "/youtube/{channel_id}": youtube_channel_page,
                "/youtube/{channel_id}/{video_id}": youtube_video_page,
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
        reload=False,
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
