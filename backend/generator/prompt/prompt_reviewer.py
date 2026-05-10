from backend.data import PromptDBData
from backend.enum import JobsStatusEnum
from backend.generator.base_generator import BaseGenerator
from backend.manager import PromptManager
from backend.prompt_agent.youtube_short_speech_generation_prompt.youtube_short_speech_generation_prompt_agent import (
    YouTubeShortSpeechGenerationPromptAgent,
)


class PromptReviewer(BaseGenerator):
    def __init__(self, job):
        super().__init__(job)
        self.prompt_manager = PromptManager()

    def generate(self) -> tuple[JobsStatusEnum, dict | None]:
        prompts = self.prompt_manager.get_prompts()
        for prompt in prompts:
            self.process_prompt(prompt=prompt)
        return JobsStatusEnum.IN_PROGRESS, None

    def process_prompt(self, prompt: PromptDBData):
        # TODO Need to run this in parallel
        YouTubeShortSpeechGenerationPromptAgent().improve()
        if prompt.comment:
            pass
