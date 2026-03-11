import logging
from typing import Any

from backend.data import (
    TaskData,
    YouTubeVideoSummarizeJobData,
)
from backend.enum import PromptTaskEnum, TaskStatusEnum
from backend.exception.app_exception import AppException
from backend.generator.base_generator import BaseGenerator
from backend.integration.agent.general_agent import GeneralAgent
from backend.manager import TaskManager, YouTubeVideoManager
from backend.services.agent_service import AgentService

logger = logging.getLogger(__name__)


class YouTubeVideoSummarizer(BaseGenerator):

    def __init__(self, task: TaskData):
        super().__init__(task)
        logger.info(f"Initializing YouTubeVideoSummarizeGenerator for video: {task.id}")
        self.job_data = YouTubeVideoSummarizeJobData.to_cls(task.payload)
        self.db_manager = YouTubeVideoManager(ref_id=self.job_data.ref_id)

    def generate(self) -> TaskStatusEnum:
        logger.info(f"Fetching transcript for video: {self.job_data.platform.video_id}")
        try:
            video = self.db_manager.get_video()
            if not video:
                logger.warning(
                    f"Video not found in DB for id: {self.job_data.platform.video_id}"
                )
                return TaskStatusEnum.COMPLETED
            if not video.transcript:
                logger.warning(
                    f"Transcript not found for video id: {self.job_data.platform.video_id}"
                )
                return TaskStatusEnum.COMPLETED
            logger.info(
                f"Successfully generated transcript and summary for video: {self.job_data.platform.video_id}"
            )
            summarize = self.__summarize_transcript(video.transcript)
            self.db_manager.update_summarized_transcript(
                video_id=self.job_data.platform.video_id,
                summarized_transcript=summarize,
            )
            self.__create_analysis_task()
            return TaskStatusEnum.COMPLETED
        except Exception as e:
            logger.error(
                f"Error processing transcript for video: {self.job_data.platform.video_id}, error: {str(e)}"
            )
            raise AppException(
                f"Error processing transcript for video: {self.job_data.platform.video_id}, error: {str(e)}"
            )

    def __summarize_transcript(self, text_transcript: str) -> Any:
        logger.debug(
            f"Summarizing transcript with length: {len(text_transcript)} characters"
        )
        service = AgentService(
            prompt_task=PromptTaskEnum.YouTubeVideoSummarization,
            task_id=str(self.task.id),
            data={
                "transcript": text_transcript,
            },
        )
        agent = GeneralAgent(
            service,
        )
        result = agent.invoke()
        return result["messages"][-1].content

    def __create_analysis_task(self):
        manager = TaskManager(self.task)
        data = manager.create_youtube_analysis_task(ref_id=self.job_data.ref_id)
        manager.add_task(data)
