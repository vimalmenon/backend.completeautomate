from backend.ui.main import main_page
from backend.ui.prompt import prompt_detail_page, prompt_page
from backend.ui.s3 import s3_bucket_page
from backend.ui.tasks import task_detail_page, tasks_page
from backend.ui.video import (
    video_detail_page,
    youtube_page,
)

__all__ = [
    "main_page",
    "youtube_page",
    "video_detail_page",
    "channel_detail_page",
    "tasks_page",
    "task_detail_page",
    "prompt_page",
    "prompt_detail_page",
    "s3_bucket_page",
]
