from abc import ABC

from backend.data import PromptDBData
from backend.enum import PromptTaskEnum
from backend.exception import AppException
from backend.manager import PromptManager


class BaseAgent(ABC):
    task: PromptTaskEnum

    def __init__(self):
        self.prompt_manager = PromptManager()

    def get_prompt(self) -> PromptDBData:
        prompt = self.prompt_manager.get_prompt_by_task(self.task)
        if not prompt:
            raise AppException(f"No prompt found with type {self.task}")
        return prompt
