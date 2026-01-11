from backend.services.helper.system_prompt.system_prompt_helper import (
    SystemPromptHelper,
)
from backend.config.enum import TeamEnum
from langchain.agents import create_agent
from backend.services.ai.deepseek_ai import DeepseekAI
from langchain.messages import SystemMessage, HumanMessage
from backend.services.agent.base_agent import BaseAgent


class ManagerAgent(BaseAgent):
    name: str = "Elara"
    role: TeamEnum = TeamEnum.MANAGER
    responsibility: str = "Overseeing team performance and project delivery"
    teams: list = [TeamEnum.SCRUM_MASTER, TeamEnum.RESEARCHER]

    def __init__(self):
        self.system_prompt = SystemPromptHelper(
            role=self.role, teams=self.teams
        ).get_system_prompt()
        self.model = DeepseekAI().get_model()

    def start_task(self, task: str):
        agent = create_agent(
            name=self.name,
            model=self.model,
            system_prompt=self.system_prompt,
        )
        messages = [
            SystemMessage(
                content="You are a manager agent. Your role is to oversee team performance and project delivery."
            ),
            HumanMessage(content=task),
        ]
        result = agent.invoke(
            {
                "messages": messages,
                "user_preferences": {"style": "technical", "verbosity": "detailed"},
            }
        )
        return result

    def resume_task(self, task_id: str):
        pass
