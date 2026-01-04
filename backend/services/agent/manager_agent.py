from backend.services.utility.system_prompt.system_prompt_utility import (
    SystemPromptUtility,
)
from backend.config.enum import TeamEnum
from langchain.agents import create_agent
from backend.services.ai.deepseek_ai import DeepseekAI


class ManagerAgent:
    name: str = "Elara"
    role: TeamEnum = TeamEnum.MANAGER
    responsibility: str = "Overseeing team performance and project delivery"
    teams: list = [TeamEnum.SCRUM_MASTER, TeamEnum.RESEARCHER]

    def __init__(self):
        system_prompt = SystemPromptUtility(
            role=self.role, teams=self.teams
        ).get_system_prompt()
        model = DeepseekAI().get_model()

        agent = create_agent(
            name=self.name,
            model=model,
            system_prompt=system_prompt,
        )
        # result = agent.invoke(
        #     {
        #         "messages": [
        #             {"role": "user", "content": "I prefer technical explanations"}
        #         ],
        #         "user_preferences": {"style": "technical", "verbosity": "detailed"},
        #     }
        # )
        # print(result)
        # result = agent.invoke(
        #     input="You are a manager agent. Your role is to oversee team performance and project delivery."
        # )
        # print(result)

    def start_task(self, task: str):
        pass

    def continue_task(self, task_id: str):
        pass
