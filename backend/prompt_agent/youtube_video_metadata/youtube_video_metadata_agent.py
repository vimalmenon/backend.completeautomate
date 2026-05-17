from uuid import UUID

from backend.data import YouTubeVideoMetadataData
from backend.enum import PromptTaskEnum
from backend.generator.response_format import YouTubeVideoAnalyzerListResponse
from backend.integration import GeneralAgent
from backend.services.agent_service import AgentService


class YouTubeVideoMetadataAgent:
    task = PromptTaskEnum.YouTubeVideoMetadata

    def __init__(self, job_id: UUID, data: dict):
        self.service = AgentService(
            prompt_task=self.task,
            task_id=f"{job_id}_metadata",
            data=data,
        )
        self.agent = GeneralAgent(
            self.service,
            response_format=YouTubeVideoAnalyzerListResponse,
        )

    def generate(self):
        result = self.agent.invoke()
        return result.get(
            "structured_response", YouTubeVideoAnalyzerListResponse(details=[])
        )

    @staticmethod
    def get_suggestions(
        structured_response: YouTubeVideoAnalyzerListResponse,
    ) -> list[YouTubeVideoMetadataData]:
        return [
            YouTubeVideoMetadataData(
                title=d.title, description=d.description, tags=d.tags
            )
            for d in structured_response.details
        ]

    def clean_up(self):
        self.agent.clean_up_messages()
