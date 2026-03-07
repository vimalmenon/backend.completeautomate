from backend.ui.main import main_page
from backend.ui.navigation import create_nav_link, navigate_with_loading
from backend.ui.prompt import prompt_page
from backend.ui.tasks import tasks_page
from backend.ui.video import video_detail_page, youtube_page

__all__ = [
    "main_page",
    "youtube_page",
    "video_detail_page",
    "tasks_page",
    "prompt_page",
    "navigate_with_loading",
    "create_nav_link",
]
