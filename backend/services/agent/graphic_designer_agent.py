from backend.services.helper.system_prompt.system_prompt_helper import (
    SystemPromptHelper,
)
from backend.services.agent.base_agent import BaseAgent
from backend.config.enum import TeamEnum
from backend.services.ai.open_ai import OpenAI, ModelEnum
from typing import List
from langchain.agents import create_agent
from langchain.messages import SystemMessage, HumanMessage, ToolMessage
import base64
from IPython.display import Image

# https://docs.langchain.com/oss/python/integrations/chat/openai#image-generation


class GraphicDesignerAgent(BaseAgent):
    name: str = "Julia"
    role: TeamEnum = TeamEnum.GRAPHIC_DESIGNER
    teams: List[TeamEnum] = []

    def __init__(self) -> None:
        self.system_prompt = SystemPromptHelper(
            role=self.role, teams=self.teams
        ).get_system_prompt()
        self.model = OpenAI(ModelEnum.GPT_5).get_model()
        self.model = self.model.bind_tools(self.__set_image_tools())
        self.system_prompt_helper = SystemPromptHelper(role=self.role, teams=self.teams)

    def __set_image_tools(self) -> list[dict]:
        return [{"type": "image_generation", "quality": "low"}]

    def start_task(self, task: str):
        agent = create_agent(
            name=self.name,
            model=self.model,
            system_prompt=self.system_prompt,
        )
        system_message = self.system_prompt_helper.get_system_message(
            content="You are a graphic designer agent. Your role is to create compelling visual content that aligns with the company's branding guidelines and marketing strategies."
        )
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=task),
        ]
        result = agent.invoke(
            {
                "messages": messages,
                "user_preferences": {"style": "technical", "verbosity": "detailed"},
            }
        )
        breakpoint()
        return result

    def resume_task(self, task_id: str):
        pass
