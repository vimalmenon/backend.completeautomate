from langchain.agents import create_agent
from langchain.messages import SystemMessage, HumanMessage

from backend.services.utility.system_prompt.system_prompt_utility import (
    SystemPromptUtility,
)
from backend.config.enum import TeamEnum
from backend.services.ai.perplexity_ai import PerplexityAI
from backend.services.agent.base_agent import BaseAgent


class ResearcherAgent(BaseAgent):
    name = "Christopher"
    role: TeamEnum = TeamEnum.RESEARCHER
    responsibility: str = "Conducting in-depth research to gather relevant information"
    teams: list = []

    def __init__(self):
        self.system_prompt = SystemPromptUtility(
            role=self.role, teams=self.teams
        ).get_system_prompt()
        self.model = PerplexityAI().get_model()

    def start_task(self, task: str):
        agent = create_agent(
            name=self.name,
            model=self.model,
            system_prompt=self.system_prompt,
        )
        messages = [
            SystemMessage(
                content="You are a researcher agent. Your role is to conduct in-depth research to gather relevant information."
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
