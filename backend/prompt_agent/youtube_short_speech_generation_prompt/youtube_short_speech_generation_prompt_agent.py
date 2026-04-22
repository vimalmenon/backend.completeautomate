from backend.data import YouTubeShortDBData
from backend.enum import PromptTaskEnum
from backend.exception import AppException
from backend.manager import PromptManager


class YouTubeShortSpeechGenerationPromptAgent:
    type = PromptTaskEnum.YouTubeShortSpeechGenerationPrompt

    def __init__(self):
        self.db_manager = PromptManager()

    def generate(self, video_short: YouTubeShortDBData):
        prompt = self.db_manager.get_prompt_by_task(self.type)
        if not prompt:
            raise AppException(f"No prompt found with type {self.type}")

    def improve(self):
        self.db_manager.get_prompt_by_task(self.type)
