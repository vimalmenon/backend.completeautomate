from backend.database import PromptDB
from backend.enum import PromptTaskEnum


class YouTubeVideoSummarizationPrompt:
    def __init__(self):
        self.prompt = PromptDB().get_prompt_by_task(
            prompt_task=PromptTaskEnum.YouTubeVideoSummarization
        )

    def generate(self):
        pass

    def review(self):
        pass
