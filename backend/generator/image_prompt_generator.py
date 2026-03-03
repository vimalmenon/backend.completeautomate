import logging
from datetime import datetime
from uuid import uuid4

from backend.data import (
    ImageGeneratorJobData,
    ImagePromptDBData,
    ImagePromptJobData,
    PromptData,
    S3Data,
    TaskData,
)
from backend.database.image.image_prompt_db import ImagePromptDB
from backend.database.task.task_db import TaskDB
from backend.enum import (
    ImageTypeEnum,
    JobEnum,
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


class ImagePromptGenerator(BaseGenerator):
    def __init__(self, task: TaskData):
        super().__init__(task)
        self.job_data = ImagePromptJobData.to_cls({**task.payload, "task_id": task.id})
        self.db_manager = ImagePromptDB()

    def generate(self) -> TaskStatusEnum:
        prompts = self.db_manager.get_by_task_id(str(self.job_data.task_id))
        if len(prompts) == 0:
            service = AgentService(
                prompt_task=PromptTaskEnum.YouTubeThumbnailImageGenerationPrompt,
                task_id=str(self.task.id),
                data={
                    "image_type": self.job_data.image_type,
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
                prompt=self.job_data.description,
                task_id=self.job_data.task_id,
                video_id=self.job_data.video_id,
                channel_id=self.job_data.channel_id,
                image_type=self.job_data.image_type,
                status=JobStatusEnum.REVIEW,
                prompts=prompt_response,
            )
            self.db_manager.save_to_db(data)
            return TaskStatusEnum.REVIEW
        elif len(prompts) == 1:
            prompt = prompts[0]
            prompt.prompts = self.__filter_prompt_responses(prompt.prompts)
            self.db_manager.update_data(prompt)
            return TaskStatusEnum.REVIEW
        else:
            logger.error(
                f"Multiple image prompt entries found for task_id {self.job_data.task_id}"
            )
            raise AppException(
                f"Multiple image prompt entries found for task_id {self.job_data.task_id}"
            )

    def __filter_prompt_responses(
        self, prompt_responses: list[PromptData]
    ) -> list[PromptData]:
        data = []
        for response in prompt_responses:
            if response.status == JobStatusEnum.CLEAN_UP:
                continue
            if response.status == JobStatusEnum.PROMOTE:
                self.__promote_to_image_generation(response)
                continue
            data.append(response)
        return data

    def __promote_to_image_generation(self, prompt_response: PromptData) -> None:
        task_id = uuid4()
        job_type = ImageGeneratorJobData(
            id=uuid4(),
            name=prompt_response.name,
            prompt=prompt_response.prompt,
            image_type=ImageTypeEnum.YouTube,
            task_id=task_id,
            data=S3Data(
                name=prompt_response.name,
                content_type=S3Data.detect_content_type_from_name(prompt_response.name),
                key=str(task_id),
            ),
        )
        task = TaskData(
            id=task_id,
            job_type=JobEnum.ImagePrompt,
            payload=job_type.to_json(),
            created_by=JobEnum.YouTubeVideo,
            created_at=datetime.now(),
            status=TaskStatusEnum.IN_PROGRESS,
            trail=self.task.trail + [self.task.id],
        )
        TaskDB().add_task(task)
