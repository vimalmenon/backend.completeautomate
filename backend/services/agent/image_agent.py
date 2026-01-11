from backend.services.helper.system_prompt.system_prompt_helper import (
    SystemPromptHelper,
)
from backend.services.agent.base_agent import BaseAgent
from backend.config.enum import TeamEnum
from backend.services.ai.open_ai import OpenAI, ModelEnum


class ImageAgent(BaseAgent):
    name = "Julia"
    role = TeamEnum.GRAPHIC_DESIGNER
    responsibility = "Designing visual content for various media"
    teams = []

    def __init__(self):
        self.system_prompt = SystemPromptHelper(
            role=self.role, teams=self.teams
        ).get_system_prompt()
        self.model = OpenAI(ModelEnum.GPT_5).get_model()

    def start_task(self, task: str):
        pass

    def resume_task(self, task_id: str):
        pass
