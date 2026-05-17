from uuid import UUID

from backend.enum import PromptTaskEnum
from backend.generator.response_format import YouTubeVideoCommunityPostsResponse
from backend.integration import GeneralAgent
from backend.services.agent_service import AgentService


class YouTubeVideoCommunityPostAgent:
    task = PromptTaskEnum.YouTubeVideoCommunityPost

    def __init__(self, job_id: UUID, data: dict):
        self.service = AgentService(
            prompt_task=self.task,
            task_id=f"{job_id}_community_post",
            data=data,
        )
        self.agent = GeneralAgent(
            self.service,
            response_format=YouTubeVideoCommunityPostsResponse,
        )

    def generate(self):
        result = self.agent.invoke()
        return result.get(
            "structured_response", YouTubeVideoCommunityPostsResponse(posts=[])
        )

    @staticmethod
    def get_posts(structured_response):
        return structured_response.posts

    def clean_up(self) -> None:
        self.agent.clean_up_messages()
