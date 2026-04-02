from backend.database import PromptDB
from backend.enum import PromptTaskEnum


class YouTubeVideoSummarizationAgent:
    task = PromptTaskEnum.YouTubeVideoSummarization

    def __init__(self):
        self.prompt = PromptDB().get_prompt_by_task(prompt_task=self.task)

    def generate(self):
        pass

    def review(self):
        pass
