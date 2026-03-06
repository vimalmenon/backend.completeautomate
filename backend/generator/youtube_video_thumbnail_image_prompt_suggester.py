import logging
from uuid import uuid4

from backend.data import (
    ImagePromptDBData,
    PromptData,
    YouTubeVideoThumbnailPromptSuggesterJobData,
)
from backend.database.image.image_prompt_db import ImagePromptDB
from backend.enum import (
    JobStatusEnum,
    PromptTaskEnum,
    TaskStatusEnum,
)
from backend.exception.app_exception import AppException
from backend.generator.base_generator import BaseGenerator
from backend.generator.response_format import ImagePromptsListRequest
from backend.integration.agent.general_agent import GeneralAgent
from backend.services.agent_service import AgentService

logger = logging.getLogger(__name__)


class YoutubeVideoThumbnailImagePromptSuggester(BaseGenerator):

    def __init__(self, task):
        super().__init__(task)
        self.job_data = YouTubeVideoThumbnailPromptSuggesterJobData.to_cls(
            {**task.payload, "task_id": task.id}
        )
        self.db_manager = ImagePromptDB()

    def generate(self) -> TaskStatusEnum:
        prompts = self.db_manager.get_by_task_id(str(self.job_data.task_id))
        if len(prompts) == 0:
            return self.__create_image_prompt_suggestion()
        return self.__update_image_prompt_suggestion(prompts)

    def __create_image_prompt_suggestion(self) -> TaskStatusEnum:
        service = AgentService(
            prompt_task=PromptTaskEnum.YouTubeThumbnailImageGenerationPrompt,
            task_id=str(self.task.id),
            data={
                "image_type": self.job_data,
            },
        )
        agent = GeneralAgent(
            service,
            response_format=ImagePromptsListRequest,
        )
        result = agent.invoke()
        structured_response = result.get("structured_response", [])
        prompt_response = [
            PromptData(
                name=data.name,
                prompt=data.prompt,
                description=data.description,
            )
            for data in structured_response.image_prompts
        ]
        data = ImagePromptDBData(
            id=uuid4(),
            ref_id=self.job_data.ref_id,
            task_id=self.job_data.task_id,
            status=JobStatusEnum.REVIEW,
            prompts=prompt_response,
        )
        self.db_manager.save_to_db(data)
        return TaskStatusEnum.REVIEW

    def __update_image_prompt_suggestion(
        self, prompts: list[ImagePromptDBData]
    ) -> TaskStatusEnum:
        if len(prompts) == 1:
            # prompt = prompts[0]
            # prompt.prompts = self.__filter_prompt_responses(prompt.prompts)
            # self.db_manager.update_data(prompt)
            return TaskStatusEnum.REVIEW

        raise AppException("There is app exception")
