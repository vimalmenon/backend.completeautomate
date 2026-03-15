from typing import Any

from backend.config.env import env
from backend.data import JobData, YouTubeVideoDBData, YouTubeVideoTaskData
from backend.enum import JobsStatusEnum, YouTubeVideoTaskEnum
from backend.exception.app_exception import AppException
from backend.generator.base_generator import BaseGeneratorJob
from backend.integration.youtube.mock_youtube_api import MockYouTubeAPI
from backend.integration.youtube.youtube_api import YouTubeAPI
from backend.manager import YouTubeVideoManager


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
        if self.task_data.task == YouTubeVideoTaskEnum.YouTubeVideoStart:
            self.__create_video_db()
            self.task_data.task = YouTubeVideoTaskEnum.YouTubeVideoFixTranscript
            return JobsStatusEnum.REVIEW, self.task_data.to_json()
        if self.task_data.task == YouTubeVideoTaskEnum.YouTubeVideoFixTranscript:
            self.__create_transcript_summary()
            self.__create_metadata_suggestions()
            self.task_data.task = YouTubeVideoTaskEnum.YouTubeVideoMetadataSelection
            return JobsStatusEnum.REVIEW, self.task_data.to_json()
        if self.task_data.task == YouTubeVideoTaskEnum.YouTubeVideoMetadataSelection:
            self.__create_thumbnail_prompt_suggestions()
            self.__generate_thumbnails()
            self.task_data.task = YouTubeVideoTaskEnum.YouTubeVideoThumbnailSelection
            return JobsStatusEnum.REVIEW, self.task_data.to_json()
        self.__upload_thumbnail()
        self.__review_video()
        self.__job_complete()
        self.task_data.task = YouTubeVideoTaskEnum.YouTubeVideoComplete
        return JobsStatusEnum.COMPLETE, self.task_data.to_json()

    def __create_video_db(self):
        if self.video_from_db:
            raise AppException("Video already exists in DB")

        youtube_response = self.youtube_api.fetch_video_details(video_id=self.video_id)
        youtube_data = YouTubeVideoDBData.to_cls_from_response(
            {**youtube_response, "ref_id": self.task_data.ref_id}
        )
        transcript = self.youtube_api.get_transcript(video_id=self.video_id)
        if transcript:
            youtube_data.transcript = self.__convert_transcript_to_text(
                result=transcript
            )
        self.youtube_manager.save_data(data=youtube_data)

    def __create_transcript_summary(self):
        pass

    def __create_metadata_suggestions(self):
        pass

    def __create_thumbnail_prompt_suggestions(self):
        pass

    def __generate_thumbnails(self):
        pass

    def __upload_thumbnail(self):
        pass

    def __review_video(self):
        pass

    def __job_complete(self):
        pass

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
