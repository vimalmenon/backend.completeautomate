from dataclasses import dataclass

from backend.data import YouTubeVideoDBData
from backend.enum import PromptTaskEnum
from backend.prompt_agent.agent.base_agent import BaseAgent


@dataclass
class State:
    video: YouTubeVideoDBData
    comment: str
    iterate: int = 0


class YouTubeThumbnailImageGenerationPromptAgent(BaseAgent):
    task = PromptTaskEnum.YouTubeThumbnailImageGenerationPrompt

    def generate(self, youtube_video: YouTubeVideoDBData):
        self.get_prompt()

    def improve(self): ...
