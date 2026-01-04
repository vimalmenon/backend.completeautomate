# from backend.services.utility.company_detail_utility import CompanyDetailUtility
from backend.config.enum import TeamEnum
from langchain.agents import create_agent
from backend.services.ai.deepseek_ai import DeepseekAI


class ManagerAgent:
    name: str = "Elara"
    role: TeamEnum = TeamEnum.MANAGER
    responsibility: str = "Overseeing team performance and project delivery"
    teams: list = ["scrum_master", "researcher"]

    def __init__(self):
        # CompanyValueUtility(
        #     role=self.role, responsibility=self.responsibility
        # ).company_values
        model = DeepseekAI().get_llm()
        agent = create_agent(
            llm=model,
            agent_type="chat-conversational-react-description",
            verbose=True,
        )
        result = agent.invoke(
            input="You are a manager agent. Your role is to oversee team performance and project delivery."
        )
        print(result)
