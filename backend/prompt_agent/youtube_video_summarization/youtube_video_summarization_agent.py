from uuid import UUID

from backend.data import YouTubeVideoDBData
from backend.database import PromptDB
from backend.enum import PromptTaskEnum
from backend.integration import GeneralAgent
from backend.services.agent_service import AgentService


class YouTubeVideoSummarizationAgent:
    task = PromptTaskEnum.YouTubeVideoSummarization

    def __init__(self, job_id: UUID, youtube_video: YouTubeVideoDBData):
        self.prompt = PromptDB().get_prompt_by_task(prompt_task=self.task)
        service = AgentService(
            prompt_task=PromptTaskEnum.YouTubeVideoSummarization,
            task_id=f"{job_id}_summarize",
            data={
                "transcript": youtube_video.transcript,
                "user_message": youtube_video.user_message,
            },
        )
        self.agent = GeneralAgent(
            service,
        )

    def generate(self):
        # self.youtube_video.summary =

        self.agent.invoke()
        return self.agent.invoke()

    def review(self):
        pass
