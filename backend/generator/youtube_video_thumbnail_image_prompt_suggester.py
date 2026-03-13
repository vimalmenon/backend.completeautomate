import logging

from backend.data import (
    ImagePromptData,
    YouTubeThumbnailImageGenerationPromptData,
    YouTubeVideoThumbnailPromptSuggesterJobData,
)
from backend.enum import (
    PromptTaskEnum,
    TaskStatusEnum,
)
from backend.exception.app_exception import AppException
from backend.generator.base_generator import BaseGenerator
from backend.generator.response_format import ImagePromptsListRequest
from backend.integration.agent.general_agent import GeneralAgent
from backend.manager import YouTubeVideoManager
from backend.services.agent_service import AgentService

logger = logging.getLogger(__name__)


class YoutubeVideoThumbnailImagePromptSuggester(BaseGenerator):

    def __init__(self, task):
        super().__init__(task)
        self.job_data = YouTubeVideoThumbnailPromptSuggesterJobData.to_cls(task.payload)
        self.video_manager = YouTubeVideoManager(ref_id=self.job_data.ref_id)
        logger.info(
            "Initialized thumbnail image prompt suggester for task_id=%s ref_id=%s",
            self.job_data.task_id,
            self.job_data.ref_id,
        )

    def generate(self) -> TaskStatusEnum:
        logger.info("Generating thumbnail image prompts for task_id=%s", self.task.id)
        video_db = self.video_manager.get_video()
        if not video_db:
            raise AppException("Not video found with the ref_id : {self.task.id}")
        if len(video_db.thumbnail_prompt_suggestions) == 0:
            return self.__create_image_prompt_suggestion()
        return self.__update_image_prompt_suggestion(
            video_db.thumbnail_prompt_suggestions
        )

    def __create_image_prompt_suggestion(self) -> TaskStatusEnum:
        logger.info(
            "Creating new thumbnail prompt suggestions for task_id=%s", self.task.id
        )
        video_data = self.video_manager.get_video()
        if not video_data:
            logger.error(
                "Video data not found for channel_id=%s video_id=%s",
                self.job_data.platform.channel_id,
                self.job_data.platform.video_id,
            )
            raise AppException("Video data not found")
        if not video_data.transcript:
            logger.error(
                "Transcript not found for channel_id=%s video_id=%s",
                self.job_data.platform.channel_id,
                self.job_data.platform.video_id,
            )
            raise AppException("Transcript not found")
        service = AgentService(
            prompt_task=PromptTaskEnum.YouTubeThumbnailImageGenerationPrompt,
            task_id=str(self.task.id),
            data=YouTubeThumbnailImageGenerationPromptData(
                title=video_data.title,
                description=video_data.description,
                video_summary=video_data.summarized_transcript or "",
            ).to_json(),
        )
        agent = GeneralAgent(
            service,
            response_format=ImagePromptsListRequest,
        )
        result = agent.invoke()
        structured_response: ImagePromptsListRequest = result.get(
            "structured_response", []
        )
        logger.debug("Agent response received for task_id=%s", self.task.id)
        prompt_response = [
            ImagePromptData(
                name=data.name,
                description=data.description,
                prompt=data.prompt,
                negative_prompt=data.negative_prompt,
            )
            for data in structured_response.image_prompts
        ]
        logger.info(
            "Prepared %d suggested prompt(s) for task_id=%s",
            len(prompt_response),
            self.task.id,
        )
        self.video_manager.update_thumbnail_prompt_suggestions(
            thumbnail_prompt_suggestions=prompt_response
        )
        # TODO REmove this
        # data = ImagePromptDBData(
        #     id=uuid4(),
        #     ref_id=self.job_data.ref_id,
        #     task_id=self.job_data.task_id,
        #     status=JobStatusEnum.REVIEW,
        #     prompts=prompt_response,
        # )
        # self.db_manager.save_to_db(data)
        logger.info("Saved thumbnail prompt suggestions for task_id=%s", self.task.id)
        return TaskStatusEnum.REVIEW

    def __update_image_prompt_suggestion(
        self, prompts: list[ImagePromptData]
    ) -> TaskStatusEnum:
        logger.info(
            "Updating thumbnail prompt suggestions for task_id=%s with %d record(s)",
            self.task.id,
            len(prompts),
        )
        if len(prompts) == 1:
            # prompt = prompts[0]
            # prompt.prompts = self.__filter_prompt_responses(prompt.prompts)
            # self.db_manager.update_data(prompt)
            logger.info(
                "Single prompt record found for task_id=%s; returning REVIEW",
                self.task.id,
            )
            return TaskStatusEnum.REVIEW

        logger.error(
            "Invalid prompt record count=%d for task_id=%s",
            len(prompts),
            self.task.id,
        )
        raise AppException("There is app exception")

    # def __fetch_video_details(self):
    #     video_db = YouTubeVideoDB()
    #     video_details = video_db.
    #     return video_details
