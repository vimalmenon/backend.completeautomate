import logging
from datetime import datetime, timedelta
from typing import Any

from backend.config.env import env
from backend.data import (
    ImagePromptData,
    JobData,
    S3Data,
    YouTubeThumbnailImageGenerationPromptData,
    YouTubeVideoDBData,
    YouTubeVideoMetadataData,
    YouTubeVideoTaskData,
    YouTubeVideoThumbnailData,
)
from backend.enum import (
    JobsStatusEnum,
    JobStatusEnum,
    PromptTaskEnum,
    YouTubeVideoTaskEnum,
)
from backend.exception.app_exception import AppException
from backend.generator.base_generator import BaseGeneratorJob
from backend.generator.response_format import (
    ImagePromptsListRequest,
    YouTubeVideoAnalyzerListResponse,
)
from backend.integration import GeneralAgent, S3Storage, YouTubeAPI
from backend.integration.youtube.mock_youtube_api import MockYouTubeAPI
from backend.manager import YouTubeVideoManager
from backend.services.agent_service import AgentImageService, AgentService

logger = logging.getLogger(__name__)


class YouTubeVideoGenerator(BaseGeneratorJob):

    def __init__(self, job: JobData):
        super().__init__(job=job)
        self.task_data = YouTubeVideoTaskData.to_cls(data=job.task_data)
        self.youtube_api: YouTubeAPI | MockYouTubeAPI = (
            MockYouTubeAPI() if env.OFFLINE else YouTubeAPI()
        )
        self.video_id = self.task_data.platform.video_id
        self.youtube_manager = YouTubeVideoManager(ref_id=self.task_data.ref_id)
        self.video_from_db = self.youtube_manager.get_video()

    def generate(self) -> tuple[JobsStatusEnum, dict]:
        logger.info(
            "Starting YouTube video generator for job %s with task %s",
            self.job.id,
            self.task_data.task.value,
        )
        if self.task_data.task == YouTubeVideoTaskEnum.YouTubeVideoStart:
            return self.__create_video_db()
        if not self.video_from_db:
            raise AppException("There is no video available")
        if self.__check_if_video_is_older_than_two_weeks(
            self.video_from_db.published_at
        ):
            logger.info("Skipping old video for job %s", self.job.id)
            return self.__job_complete()
        if self.task_data.task == YouTubeVideoTaskEnum.YouTubeVideoFixTranscript:
            logger.info("Creating transcript summary for job %s", self.job.id)
            self.__create_transcript_summary(video_from_db=self.video_from_db)
            return self.__create_metadata_suggestions(video_from_db=self.video_from_db)
        if self.task_data.task == YouTubeVideoTaskEnum.YouTubeVideoMetadataSelection:
            logger.info("Creating thumbnails for job %s", self.job.id)
            self.__create_thumbnail_prompt_suggestions(video_from_db=self.video_from_db)
            return self.__generate_thumbnails(video_from_db=self.video_from_db)
        logger.info("Uploading thumbnail and reviewing video for job %s", self.job.id)
        self.__upload_thumbnail(video_from_db=self.video_from_db)
        self.__review_video(video_from_db=self.video_from_db)
        return self.__job_complete()

    def __check_if_video_is_older_than_two_weeks(self, published_at: datetime) -> bool:
        current_time = (
            datetime.now(tz=published_at.tzinfo)
            if published_at.tzinfo is not None
            else datetime.now()
        )
        delta = current_time - published_at
        return delta >= timedelta(weeks=2)

    def __create_video_db(self) -> tuple[JobsStatusEnum, dict]:
        if self.video_from_db:
            raise AppException("Video already exists in DB")

        logger.info("Fetching YouTube video details for video %s", self.video_id)
        youtube_response = self.youtube_api.fetch_video_details(video_id=self.video_id)
        youtube_data = YouTubeVideoDBData.to_cls_from_response(
            {**youtube_response, "ref_id": self.task_data.ref_id}
        )
        transcript = self.youtube_api.get_transcript(video_id=self.video_id)
        if transcript:
            logger.info("Transcript found for video %s", self.video_id)
            youtube_data.transcript = self.__convert_transcript_to_text(
                result=transcript
            )
            self.youtube_manager.save_data(data=youtube_data)
            self.task_data.task = YouTubeVideoTaskEnum.YouTubeVideoFixTranscript
            return JobsStatusEnum.REVIEW, self.task_data.to_json()
        logger.info(
            "Transcript missing for video %s; saving video and moving to review",
            self.video_id,
        )
        self.youtube_manager.save_data(data=youtube_data)
        self.task_data.task = YouTubeVideoTaskEnum.YouTubeVideoComplete
        return JobsStatusEnum.COMPLETE, self.task_data.to_json()

    def __create_transcript_summary(self, video_from_db: YouTubeVideoDBData) -> None:
        if not video_from_db.transcript:
            raise AppException("Transcript not found")
        logger.info("Summarizing transcript for job %s", self.job.id)
        summarize = self.__summarize_transcript(video_from_db.transcript)
        self.youtube_manager.update_summarized_transcript(
            summarized_transcript=summarize,
        )

    def __summarize_transcript(self, text_transcript: str) -> Any:
        service = AgentService(
            prompt_task=PromptTaskEnum.YouTubeVideoSummarization,
            task_id=f"{str(self.job.id)}_summarize",
            data={
                "transcript": text_transcript,
            },
        )
        agent = GeneralAgent(
            service,
        )
        result = agent.invoke()
        # TODO Need to get it reviewed by AI 2 times
        return result["messages"][-1].content

    def __create_metadata_suggestions(
        self, video_from_db: YouTubeVideoDBData
    ) -> tuple[JobsStatusEnum, dict]:
        logger.info("Generating metadata suggestions for job %s", self.job.id)
        service = AgentService(
            prompt_task=PromptTaskEnum.YouTubeVideoAnalysis,
            task_id=f"{str(self.job.id)}_metadata",
            data={
                "transcript": video_from_db.summarized_transcript,
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
        self.youtube_manager.update_metadata_suggestions(video_metadata_suggestions)
        self.task_data.task = YouTubeVideoTaskEnum.YouTubeVideoMetadataSelection
        logger.info(
            "Stored %s metadata suggestions for job %s",
            len(video_metadata_suggestions),
            self.job.id,
        )
        return JobsStatusEnum.REVIEW, self.task_data.to_json()

    def __create_thumbnail_prompt_suggestions(self, video_from_db: YouTubeVideoDBData):
        logger.info("Generating thumbnail prompt suggestions for job %s", self.job.id)
        service = AgentService(
            prompt_task=PromptTaskEnum.YouTubeThumbnailImageGenerationPrompt,
            task_id=f"{str(self.job.id)}_thumbnail",
            data=YouTubeThumbnailImageGenerationPromptData(
                title=video_from_db.title,
                description=video_from_db.description,
                video_summary=video_from_db.summarized_transcript or "",
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
        prompt_response = [
            ImagePromptData(
                name=data.name,
                description=data.description,
                prompt=data.prompt,
                negative_prompt=data.negative_prompt,
            )
            for data in structured_response.image_prompts
        ]
        self.youtube_manager.update_thumbnail_prompt_suggestions(
            thumbnail_prompt_suggestions=prompt_response
        )
        logger.info(
            "Stored %s thumbnail prompt suggestions for job %s",
            len(prompt_response),
            self.job.id,
        )

    def __generate_thumbnails(
        self, video_from_db: YouTubeVideoDBData
    ) -> tuple[JobsStatusEnum, dict]:
        logger.info("Generating thumbnail images for job %s", self.job.id)
        thumbnails_suggestions: list[YouTubeVideoThumbnailData] = []
        for suggestion in video_from_db.thumbnail_prompt_suggestions:
            s3_data = S3Data(
                name=suggestion.name,
                content_type=S3Data.detect_content_type_from_name(suggestion.name),
                key=self.task_data.ref_id,
            )
            video_thumbnail_data = YouTubeVideoThumbnailData(
                s3_data=s3_data,
                status=JobStatusEnum.REVIEW,
            )
            service = AgentImageService(prompt=suggestion.prompt)
            agent = GeneralAgent(
                service,
                response_format=YouTubeVideoAnalyzerListResponse,
            )
            image_data = agent.generate()
            S3Storage().upload_data(s3_data=s3_data, data=image_data)
            thumbnails_suggestions.append(video_thumbnail_data)
        self.youtube_manager.update_thumbnails_suggestions(thumbnails_suggestions)
        self.task_data.task = YouTubeVideoTaskEnum.YouTubeVideoThumbnailSelection
        logger.info(
            "Generated %s thumbnail suggestions for job %s",
            len(thumbnails_suggestions),
            self.job.id,
        )
        return JobsStatusEnum.REVIEW, self.task_data.to_json()

    def __upload_thumbnail(
        self, video_from_db: YouTubeVideoDBData
    ) -> tuple[JobsStatusEnum, dict]:
        suggested_thumbnails = [
            suggestion
            for suggestion in video_from_db.thumbnails_suggestions
            if suggestion.status == JobStatusEnum.PROMOTE
        ]
        if len(suggested_thumbnails) == 1:
            thumbnail = suggested_thumbnails[0]
            logger.info("Uploading promoted thumbnail for job %s", self.job.id)
            YouTubeAPI().update_thumbnail(
                video_id=self.video_id,
                thumbnail_path=thumbnail.s3_data.downloaded_path,
            )
            self.task_data.task = YouTubeVideoTaskEnum.YouTubeVideoComplete
            return JobsStatusEnum.COMPLETE, self.task_data.to_json()
        raise AppException("More than one thumbnail was selected")

    def __review_video(self, video_from_db: YouTubeVideoDBData):
        logger.info("Reviewing YouTube video for job %s", self.job.id)
        service = AgentService(
            prompt_task=PromptTaskEnum.YouTubeVideoReview,
            task_id=f"{str(self.job.id)}_review",
            data={
                "transcript": video_from_db.transcript,
            },
        )
        agent = GeneralAgent(
            service,
        )
        result = agent.invoke()
        # TODO Need to get it reviewed by AI 2 times
        return result["messages"][-1].content

    def __job_complete(self) -> tuple[JobsStatusEnum, dict]:
        self.task_data.task = YouTubeVideoTaskEnum.YouTubeVideoComplete
        logger.info("Completed YouTube video generator for job %s", self.job.id)
        return JobsStatusEnum.COMPLETE, self.task_data.to_json()

    def __convert_transcript_to_text(self, result) -> str:
        text = [self.__process_transcript(snippet) for snippet in result.snippets]
        return "\n".join(text)

    def __process_transcript(self, snippet: Any) -> str:
        text = (
            snippet.get("text", "")
            if isinstance(snippet, dict)
            else getattr(snippet, "text", "")
        )
        start = float(
            snippet.get("start", 0.0)
            if isinstance(snippet, dict)
            else getattr(snippet, "start", 0.0)
        )
        duration = float(
            snippet.get("duration", 0.0)
            if isinstance(snippet, dict)
            else getattr(snippet, "duration", 0.0)
        )
        end = start + duration
        return f"[{start:.3f} {end:.3f}] {text}"
