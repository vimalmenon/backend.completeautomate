from backend.services.helper.system_prompt.system_prompt_helper import (
    SystemPromptHelper,
)
from backend.services.agent.base_agent import BaseAgent
from backend.config.enum import TeamEnum
from backend.services.ai.open_ai import OpenAI, ModelEnum
from typing import List


# https://docs.langchain.com/oss/python/integrations/chat/openai#image-generation


class GraphicDesignerAgent(BaseAgent):
    name: str = "Julia"
    role: TeamEnum = TeamEnum.GRAPHIC_DESIGNER
    responsibility: str = "Designing visual content for various media"
    teams: List[TeamEnum] = []

    def __init__(self) -> None:
        self.system_prompt = SystemPromptHelper(
            role=self.role, teams=self.teams
        ).get_system_prompt()
        self.model = OpenAI(ModelEnum.GPT_5).get_model()
        self.model = self.model.bind_tools(self.__set_image_tools())

    def __set_image_tools(self) -> list[dict]:
        return [{"type": "image_generation", "quality": "low"}]

    def start_task(self, task: str):
        pass

    def resume_task(self, task_id: str):
        pass
