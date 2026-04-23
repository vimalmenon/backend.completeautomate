from backend.data import YouTubeShortDBData
from backend.enum import PromptTaskEnum
from backend.prompt_agent.agent.base_agent import BaseAgent


class YouTubeShortSpeechGenerationPromptAgent(BaseAgent):
    task = PromptTaskEnum.YouTubeShortSpeechGenerationPrompt

    def generate(self, video_short: YouTubeShortDBData):
        self.get_prompt()

    def improve(self): ...

    def __test(self): ...

    def __reflect(self): ...
