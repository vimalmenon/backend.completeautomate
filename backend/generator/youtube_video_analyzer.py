import logging

from backend.data import (
    TaskData,
    YouTubeVideoAnalysisDBData,
    YouTubeVideoDetailDBData,
    YouTubeVideoSummarizeJobData,
)
from backend.database import YouTubeVideoAnalysisDB, YouTubeVideoDB
from backend.enum import PromptTaskEnum, TaskStatusEnum
from backend.exception.app_exception import AppException
from backend.generator.base_generator import BaseGenerator
from backend.generator.response_format import YouTubeVideoAnalyzerListResponse
from backend.integration.agent.general_agent import GeneralAgent
from backend.services.agent_service import AgentService

logger = logging.getLogger(__name__)


class YouTubeVideoAnalyzer(BaseGenerator):
    def __init__(self, task: TaskData):
        super().__init__(task)
        self.job_data = YouTubeVideoSummarizeJobData.to_cls(task.payload)
        self.video_db = YouTubeVideoDB(self.job_data.channel_id)
        self.analysis_db = YouTubeVideoAnalysisDB()
        logger.info("Initializing YouTubeVideoAnalyzerGenerator")

    def generate(self) -> TaskStatusEnum:
        video_db = self.video_db.fetch_video_from_db(self.job_data.video_id)
        if not video_db:
            logger.error("Video not found for video_id: %s", self.job_data.video_id)
            raise AppException(f"Video not found for video_id {self.job_data.video_id}")
        if not video_db.transcript:
            logger.warning(
                "Transcript not found for video_id: %s", self.job_data.video_id
            )
            return TaskStatusEnum.COMPLETED

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
        structured_response = result.get("structured_response", [])
        video_details = [
            YouTubeVideoDetailDBData(
                title=data.title,
                description=data.description,
                status=data.status,
                tags=data.tags,
            )
            for data in structured_response.image_prompts
        ]
        data = YouTubeVideoAnalysisDBData(
            video_id=self.job_data.video_id,
            channel_id=self.job_data.channel_id,
            ref_id=self.job_data.ref_id,
            task_id=self.task.id,
            video_details=video_details,
        )
        self.analysis_db.add_data(data)
        logger.info("Successfully analyzed video data for task id: %s", self.task.id)
        return TaskStatusEnum.REVIEW
