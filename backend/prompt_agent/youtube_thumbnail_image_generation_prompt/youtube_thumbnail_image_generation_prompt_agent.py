from uuid import UUID

from backend.data import ImagePromptData
from backend.enum import PromptTaskEnum
from backend.generator.response_format import ImagePromptsListRequest
from backend.integration import GeneralAgent
from backend.services.agent_service import AgentService


class YouTubeThumbnailImageGenerationPromptAgent:
    task = PromptTaskEnum.YouTubeThumbnailImageGenerationPrompt

    def __init__(self, job_id: UUID, data: dict):
        self.service = AgentService(
            prompt_task=self.task,
            task_id=f"{job_id}_thumbnail",
            data=data,
        )
        self.agent = GeneralAgent(
            self.service,
            response_format=ImagePromptsListRequest,
        )

    def generate(self):
        result = self.agent.invoke()
        return result.get(
            "structured_response", ImagePromptsListRequest(image_prompts=[])
        )

    @staticmethod
    def get_prompts(structured_response) -> list[ImagePromptData]:
        return [
            ImagePromptData(
                name=d.name,
                description=d.description,
                prompt=d.prompt,
                negative_prompt=d.negative_prompt,
            )
            for d in structured_response.image_prompts
        ]

    def clean_up(self) -> None:
        self.agent.clean_up_messages()
