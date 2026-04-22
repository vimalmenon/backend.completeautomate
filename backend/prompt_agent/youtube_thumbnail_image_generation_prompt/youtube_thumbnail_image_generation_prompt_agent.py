from backend.data import YouTubeVideoDBData
from backend.enum import PromptTaskEnum
from backend.prompt_agent.agent.base_agent import BaseAgent


class YouTubeThumbnailImageGenerationPromptAgent(BaseAgent):
    task = PromptTaskEnum.YouTubeThumbnailImageGenerationPrompt

    def generate(self, youtube_video: YouTubeVideoDBData):
        self.get_prompt()

    def improve(self): ...
