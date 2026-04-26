from backend.data import YouTubeVideoDBData
from backend.enum import PromptTaskEnum
from backend.prompt_agent.agent.base_agent import BaseAgent


class YouTubeVideoTwitterPostAgent(BaseAgent):
    task = PromptTaskEnum.YouTubeVideoTwitterPost

    def generate(self, data: YouTubeVideoDBData):
        self.get_prompt()
