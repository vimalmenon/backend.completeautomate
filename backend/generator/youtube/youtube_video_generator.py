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
    YouTubeVideoTaskData,
    YouTubeVideoThumbnailData,
)
from backend.enum import (
    JobsStatusEnum,
    PromptTaskEnum,
    YouTubeVideoTaskEnum,
)
from backend.exception import AppException
from backend.generator.base_generator import BaseGenerator
from backend.generator.response_format import (
    ImagePromptsListRequest,
    YouTubeVideoAnalyzerListResponse,
    YouTubeVideoCommunityPostsResponse,
)
from backend.integration import GeneralAgent, S3Storage, YouTubeAPI
from backend.integration.youtube.mock_youtube_api import MockYouTubeAPI
from backend.manager import JobManager, YouTubeVideoManager
from backend.services.agent_service import AgentImageService, AgentService

logger = logging.getLogger(__name__)


class YouTubeVideoGenerator(BaseGenerator):

    def __init__(self, job: JobData):
        super().__init__(job=job)
        self.task_data = YouTubeVideoTaskData.to_cls(data=job.task_data)
        self.youtube_api: YouTubeAPI | MockYouTubeAPI = (
            MockYouTubeAPI() if env.OFFLINE else YouTubeAPI()
        )
        self.s3_storage = S3Storage()
        self.video_id = self.task_data.platform.video_id
        self.youtube_manager = YouTubeVideoManager(ref_id=self.task_data.ref_id)
        self.video_from_db = self.youtube_manager.get_video()
        self.job_manager = JobManager()

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
            self.__update_metadata_selected(video_from_db=self.video_from_db)
            self.__create_thumbnail_prompt_suggestions(video_from_db=self.video_from_db)
            return self.__generate_thumbnails(video_from_db=self.video_from_db)
        if self.task_data.task == YouTubeVideoTaskEnum.YouTubeVideoThumbnailSelection:
            logger.info(
                "Uploading thumbnail and reviewing video for job %s", self.job.id
            )
            self.__upload_thumbnail(video_from_db=self.video_from_db)
            self.__create_community_post(video_from_db=self.video_from_db)
            return self.__job_complete()
        raise AppException("Invalid task for YouTube video generator")

    def __check_if_video_is_older_than_two_weeks(self, published_at: datetime) -> bool:
        current_time = (
            datetime.now(tz=published_at.tzinfo)
            if published_at.tzinfo is not None
            else datetime.now()
        )
        delta = current_time - published_at
        return delta >= timedelta(weeks=2)

    def __update_metadata_selected(self, video_from_db: YouTubeVideoDBData) -> None:
        metadata_suggestions = [
            selection
            for selection in video_from_db.metadata_suggestions
            if selection.selected
        ]
        if len(metadata_suggestions) == 1:
            selected_metadata = metadata_suggestions[0]
            self.youtube_api.update_video_metadata(
                video_id=self.video_id,
                title=selected_metadata.title,
                description=selected_metadata.description,
                tags=selected_metadata.tags,
            )
            video_from_db.title = selected_metadata.title
            video_from_db.description = selected_metadata.description
            video_from_db.tags = selected_metadata.tags
            self.youtube_manager.update_metadata(
                title=selected_metadata.title,
                description=selected_metadata.description,
                tags=selected_metadata.tags,
            )
            self.youtube_manager.update_metadata_suggestions(metadata_suggestions=[])
        else:
            raise AppException("More than one metadata suggestion was selected")

    def __create_video_db(self) -> tuple[JobsStatusEnum, dict]:
        if self.video_from_db:
            raise AppException("Video already exists in DB")

        logger.info("Fetching YouTube video details for video %s", self.video_id)
        youtube_response = self.youtube_api.fetch_video_details(video_id=self.video_id)
        youtube_data = YouTubeVideoDBData.to_cls_from_response(
            {
                **youtube_response,
                "ref_id": self.task_data.ref_id,
                "task_status": YouTubeVideoTaskEnum.YouTubeVideoStart.value,
            }
        )
        transcript = self.youtube_api.get_transcript(video_id=self.video_id)
        if transcript:
            logger.info("Transcript found for video %s", self.video_id)
            youtube_data.transcript = self.__convert_transcript_to_text(
                result=transcript
            )
            youtube_data.task_status = YouTubeVideoTaskEnum.YouTubeVideoFixTranscript
            self.youtube_manager.save_data(data=youtube_data)
            self.task_data.task = YouTubeVideoTaskEnum.YouTubeVideoFixTranscript
            return JobsStatusEnum.REVIEW, self.task_data.to_json()
        logger.info(
            "Transcript missing for video %s; saving video and moving to review",
            self.video_id,
        )
        youtube_data.task_status = YouTubeVideoTaskEnum.YouTubeVideoComplete
        self.youtube_manager.save_data(data=youtube_data)
        self.task_data.task = YouTubeVideoTaskEnum.YouTubeVideoComplete
        return JobsStatusEnum.COMPLETE, self.task_data.to_json()

    def __create_transcript_summary(self, video_from_db: YouTubeVideoDBData) -> None:
        if video_from_db.transcript and video_from_db.user_message:
            logger.info("Summarizing transcript for job %s", self.job.id)
            summarize = self.__summarize_transcript(
                video_from_db.transcript, video_from_db.user_message
            )
            self.youtube_manager.update_summarized_transcript(
                summarized_transcript=summarize,
            )
        raise AppException("Transcript not found")

    def __summarize_transcript(self, text_transcript: str, user_message: str) -> Any:
        service = AgentService(
            prompt_task=PromptTaskEnum.YouTubeVideoSummarization,
            task_id=f"{str(self.job.id)}_summarize",
            data={"transcript": text_transcript, "user_message": user_message},
        )
        agent = GeneralAgent(
            service,
        )
        result = agent.invoke()

        # # TODO Need to get it reviewed one more time
        # result = agent.reinvoke(message="Go trough the result one more time")

        return result["messages"][-1].content

    def __create_metadata_suggestions(
        self, video_from_db: YouTubeVideoDBData
    ) -> tuple[JobsStatusEnum, dict]:
        logger.info("Generating metadata suggestions for job %s", self.job.id)
        from backend.prompt_agent import YouTubeVideoMetadataAgent

        agent = YouTubeVideoMetadataAgent(
            job_id=self.job.id,
            data={
                "transcript": video_from_db.summarized_transcript,
                "user_message": video_from_db.user_message,
            },
        )
        structured_response = agent.generate()
        video_metadata_suggestions = YouTubeVideoMetadataAgent.get_suggestions(
            structured_response
        )
        self.youtube_manager.update_metadata_suggestions(video_metadata_suggestions)
        self.youtube_manager.update_task_status(
            task_status=YouTubeVideoTaskEnum.YouTubeVideoMetadataSelection
        )
        self.task_data.task = YouTubeVideoTaskEnum.YouTubeVideoMetadataSelection
        agent.clean_up()
        logger.info(
            "Stored %s metadata suggestions for job %s",
            len(video_metadata_suggestions),
            self.job.id,
        )
        return JobsStatusEnum.REVIEW, self.task_data.to_json()

    def __create_thumbnail_prompt_suggestions(
        self, video_from_db: YouTubeVideoDBData
    ) -> None:
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

        # result = agent.reinvoke(message="Go trough the result one more time")

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
        agent.clean_up_messages()

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
        self.youtube_manager.update_task_status(
            task_status=YouTubeVideoTaskEnum.YouTubeVideoThumbnailSelection
        )
        self.task_data.task = YouTubeVideoTaskEnum.YouTubeVideoThumbnailSelection
        logger.info(
            "Generated %s thumbnail suggestions for job %s",
            len(thumbnails_suggestions),
            self.job.id,
        )
        return JobsStatusEnum.REVIEW, self.task_data.to_json()

    def __upload_thumbnail(self, video_from_db: YouTubeVideoDBData) -> None:
        suggested_thumbnails = [
            suggestion
            for suggestion in video_from_db.thumbnails_suggestions
            if suggestion.selected
        ]
        if len(suggested_thumbnails) == 1:
            thumbnail = suggested_thumbnails[0]
            logger.info("Uploading promoted thumbnail for job %s", self.job.id)
            S3Storage().download_data(data=thumbnail.s3_data)
            self.youtube_api.update_thumbnail(
                video_id=self.video_id,
                thumbnail_path=thumbnail.s3_data.downloaded_path,
            )
            youtube_response = self.youtube_api.fetch_video_details(
                video_id=self.video_id
            )
            updated_youtube_response = video_from_db.to_cls_from_response(
                {
                    **youtube_response,
                    "ref_id": self.task_data.ref_id,
                    "task_status": YouTubeVideoTaskEnum.YouTubeVideoCommunityPost.value,
                }
            )
            self.youtube_manager.update_thumbnail(
                thumbnail_url=updated_youtube_response.thumbnail
            )
        raise AppException("More than one thumbnail was selected")

    def __create_community_post(self, video_from_db: YouTubeVideoDBData) -> None:
        service = AgentService(
            prompt_task=PromptTaskEnum.YouTubeVideoCommunityPost,
            task_id=f"{str(self.job.id)}_community_post",
            data=YouTubeThumbnailImageGenerationPromptData(
                title=video_from_db.title,
                description=video_from_db.description,
                video_summary=video_from_db.summarized_transcript or "",
            ).to_json(),
        )
        agent = GeneralAgent(
            service,
            response_format=YouTubeVideoCommunityPostsResponse,
        )
        result = agent.invoke()

        structured_response: YouTubeVideoCommunityPostsResponse = result.get(
            "structured_response", []
        )
        self.youtube_manager.update_community_posts(
            community_posts=structured_response.posts
        )
        agent.clean_up_messages()

    def __job_complete(self) -> tuple[JobsStatusEnum, dict]:
        self.youtube_manager.update_task_status(
            task_status=YouTubeVideoTaskEnum.YouTubeVideoComplete
        )
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
