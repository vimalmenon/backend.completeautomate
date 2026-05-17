from uuid import UUID

from backend.enum import PromptTaskEnum
from backend.integration import GeneralAgent
from backend.services.agent_service import AgentService


class YouTubeVideoSummarizationAgent:
    task = PromptTaskEnum.YouTubeVideoSummarization

    def __init__(self, job_id: UUID, data: dict):
        self.service = AgentService(
            prompt_task=self.task,
            task_id=f"{job_id}_summarize",
            data=data,
        )
        self.agent = GeneralAgent(self.service)

    def generate(self) -> str:
        result = self.agent.invoke()
        return result["messages"][-1].content

    def clean_up(self) -> None:
        self.agent.clean_up_messages()
