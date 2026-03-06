import logging

from backend.data import (
    TaskData,
    YouTubeVideoDBData,
    YouTubeVideoDetailDBData,
    YouTubeVideoMetadataDBData,
    YouTubeVideoSummarizeJobData,
)
from backend.database import YouTubeVideoDB, YouTubeVideoMetadataSuggesterDB
from backend.enum import JobStatusEnum, PromptTaskEnum, TaskStatusEnum
from backend.exception.app_exception import AppException
from backend.generator.base_generator import BaseGenerator
from backend.generator.response_format import YouTubeVideoAnalyzerListResponse
from backend.integration.agent.general_agent import GeneralAgent
from backend.services.agent_service import AgentService

logger = logging.getLogger(__name__)


class YouTubeVideoMetadataSuggester(BaseGenerator):
    def __init__(self, task: TaskData):
        super().__init__(task)
        self.job_data = YouTubeVideoSummarizeJobData.to_cls(task.payload)
        self.channel_id = self.job_data.platform.channel_id
        self.video_db = YouTubeVideoDB(self.channel_id)
        self.analysis_db = YouTubeVideoMetadataSuggesterDB()
        logger.info("Initializing YouTubeVideoAnalyzerGenerator")

    def generate(self) -> TaskStatusEnum:
        video_db = self.video_db.fetch_video_from_db(self.job_data.platform.video_id)
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
        suggested_video = self.analysis_db.fetch_suggestion(
            self.job_data.platform.channel_id, self.job_data.platform.video_id
        )
        if not suggested_video:
            return self.__create_metadata_suggestion(video_db)
        return self.__check_suggested_video(suggested_video)

    def __create_metadata_suggestion(
        self, video_db: YouTubeVideoDBData
    ) -> TaskStatusEnum:
        logger.info("Analyzing video data for task id: %s", self.task.id)
        service = AgentService(
            prompt_task=PromptTaskEnum.YouTubeVideoAnalysis,
            task_id=str(self.task.id),
            data={
                "transcript": video_db.transcript.summarize,
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

        video_details = [
            YouTubeVideoDetailDBData(
                title=data.title,
                description=data.description,
                status=JobStatusEnum.REVIEW,
                tags=data.tags,
            )
            for data in structured_response.details
        ]
        data = YouTubeVideoMetadataDBData(
            ref_id=self.job_data.ref_id,
            task_id=self.task.id,
            video_details=video_details,
        )
        self.analysis_db.add_data(data)
        logger.info("Successfully analyzed video data for task id: %s", self.task.id)
        return TaskStatusEnum.REVIEW

    def __check_suggested_video(
        self, suggested_video: YouTubeVideoMetadataDBData
    ) -> TaskStatusEnum:
        if suggested_video.comment:
            # TODO Need Agent to review
            return TaskStatusEnum.REVIEW
        promoted_videos = [
            detail.status == JobStatusEnum.PROMOTE
            for detail in suggested_video.video_details
        ]
        if len(promoted_videos) == 1:
            # TODO Move the job to task
            return TaskStatusEnum.REVIEW
        raise AppException("There is app exception")
