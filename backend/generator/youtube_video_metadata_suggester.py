import logging

from backend.data import (
    TaskData,
    YouTubeVideoDBData,
    YouTubeVideoMetadataData,
    YouTubeVideoSummarizeJobData,
)
from backend.database import YouTubeVideoDB
from backend.enum import JobStatusEnum, PromptTaskEnum, TaskStatusEnum
from backend.exception.app_exception import AppException
from backend.generator.base_generator import BaseGenerator
from backend.generator.response_format import YouTubeVideoAnalyzerListResponse
from backend.integration.agent.general_agent import GeneralAgent
from backend.manager import TaskManager, YouTubeVideoManager
from backend.services.agent_service import AgentService

logger = logging.getLogger(__name__)


class YouTubeVideoMetadataSuggester(BaseGenerator):
    def __init__(self, task: TaskData):
        super().__init__(task)
        self.job_data = YouTubeVideoSummarizeJobData.to_cls(task.payload)
        self.channel_id = self.job_data.platform.channel_id
        self.video_db = YouTubeVideoDB(ref_id=self.job_data.ref_id)
        self.video_manager = YouTubeVideoManager(ref_id=self.job_data.ref_id)
        logger.info("Initializing YouTubeVideoAnalyzerGenerator")

    def generate(self) -> TaskStatusEnum:
        video_db = self.video_db.fetch_video_from_db()
        if not video_db:
            logger.error(
                "Video not found for video_id: %s", self.job_data.platform.video_id
            )
            raise AppException(
                f"Video not found for video_id {self.job_data.platform.video_id}"
            )
        if not video_db.transcript:
            logger.warning(
                "Transcript not found for video_id: %s", self.job_data.platform.video_id
            )
            return TaskStatusEnum.COMPLETED
        if not video_db.metadata_suggestions:
            return self.__create_metadata_suggestion(video_db)
        return self.__check_suggested_video(video_db)

    def __create_metadata_suggestion(
        self, video_db: YouTubeVideoDBData
    ) -> TaskStatusEnum:
        logger.info("Analyzing video data for task id: %s", self.task.id)
        assert video_db.transcript is not None, "Transcript should not be None"
        service = AgentService(
            prompt_task=PromptTaskEnum.YouTubeVideoAnalysis,
            task_id=str(self.task.id),
            data={
                "transcript": video_db.summarized_transcript,
            },
        )
        agent = GeneralAgent(
            service,
            response_format=YouTubeVideoAnalyzerListResponse,
        )
        result = agent.invoke()
        structured_response: YouTubeVideoAnalyzerListResponse = result.get(
            "structured_response", YouTubeVideoAnalyzerListResponse(details=[])
        )
        video_metadata_suggestions = [
            YouTubeVideoMetadataData(
                title=data.title,
                description=data.description,
                tags=data.tags,
                status=JobStatusEnum.REVIEW,
            )
            for data in structured_response.details
        ]
        self.video_manager.update_metadata_suggestions(video_metadata_suggestions)
        logger.info("Successfully analyzed video data for task id: %s", self.task.id)
        return TaskStatusEnum.REVIEW

    def __check_suggested_video(self, video_db: YouTubeVideoDBData) -> TaskStatusEnum:
        if video_db.comment:
            # TODO Need Agent to review
            return TaskStatusEnum.REVIEW
        promoted_videos = [
            detail
            for detail in video_db.metadata_suggestions
            if detail.status == JobStatusEnum.PROMOTE
        ]
        if len(promoted_videos) == 1:
            promoted_video = promoted_videos[0]
            task_manager = TaskManager(self.task)
            task = task_manager.create_youtube_metadata_updater_task(
                ref_id=self.job_data.ref_id,
                title=promoted_video.title,
                description=promoted_video.description,
                tags=promoted_video.tags,
            )
            task_manager.add_task(task)
            return TaskStatusEnum.COMPLETED
        raise AppException("There is app exception")
