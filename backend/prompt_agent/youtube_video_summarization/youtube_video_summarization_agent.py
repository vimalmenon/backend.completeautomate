from backend.database import PromptDB
from backend.enum import PromptTaskEnum
from backend.integration import GeneralAgent
from backend.services.agent_service import AgentService


class YouTubeVideoSummarizationAgent:
    task = PromptTaskEnum.YouTubeVideoSummarization

    def __init__(self, text_transcript: str, user_message: str):
        self.prompt = PromptDB().get_prompt_by_task(prompt_task=self.task)
        service = AgentService(
            prompt_task=PromptTaskEnum.YouTubeVideoSummarization,
            task_id=f"{str(self.job.id)}_summarize",
            data={"transcript": text_transcript, "user_message": user_message},
        )
        self.agent = GeneralAgent(
            service,
        )

    def generate(self):
        return self.agent.invoke()

    def review(self):
        pass
