from backend.data import YouTubeVideoDBData
from backend.enum import PromptTaskEnum
from backend.exception import AppException
from backend.manager import PromptManager


class YouTubeThumbnailImageGenerationPromptAgent:
    task = PromptTaskEnum.YouTubeThumbnailImageGenerationPrompt

    def __init__(self):
        self.prompt_manager = PromptManager()

    def generate(self, youtube_video: YouTubeVideoDBData):
        prompt = self.db_manager.get_prompt_by_task(self.type)
        if not prompt:
            raise AppException(f"No prompt found with type {self.type}")

    def improve(self):
        pass
