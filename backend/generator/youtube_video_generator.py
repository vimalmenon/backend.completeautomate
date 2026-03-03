import logging
from datetime import datetime
from uuid import uuid4

from backend.data import (
    PlatformDBData,
    PlatformYouTubeVideoDBData,
    TaskData,
    YouTubeVideoDBData,
    YouTubeVideoJobData,
    YouTubeVideoSummarizeJobData,
)
from backend.database import PlatformDB, TaskDB, YouTubeVideoDB
from backend.enum import JobEnum, PlatformEnum, TaskStatusEnum
from backend.generator.base_generator import BaseGenerator
from backend.integration.youtube.youtube_api import YouTubeAPI

logger = logging.getLogger(__name__)


class YouTubeVideoGenerator(BaseGenerator):

    def __init__(self, task: TaskData):
        super().__init__(task)
        logger.info("Initializing YouTubeVideoGenerator")
        self.youtube_api = YouTubeAPI()
        self.job_data = YouTubeVideoJobData.to_cls(task.payload)
        self.db = YouTubeVideoDB(self.job_data.platform.channel_id)

    def generate(self) -> TaskStatusEnum:
        logger.info(
            "Fetching videos for channel id: %s",
            self.job_data.platform.channel_id,
        )
        videos = YouTubeAPI().list_all_videos(self.job_data.platform.channel_id)
        logger.info("Found %s videos to process", len(videos))
        for video in videos:
            self.__update_video(video["id"])
        return TaskStatusEnum.IN_PROGRESS

    def __update_video(self, video_id: str) -> None:
        logger.info("Updating video data for id: %s", video_id)
        video_from_db = self.db.fetch_video_from_db(video_id)
        if not video_from_db:
            logger.info("Video not found in DB. Fetching details from API.")
            youtube_response = self.youtube_api.fetch_video_details(video_id)
            ref_id = self.__create_platform_data(video_id)

            youtube_data = YouTubeVideoDBData.to_cls_from_response(
                {**youtube_response, "task_id": str(self.task.id), "ref_id": ref_id}
            )
            self.db.add_video(youtube_data)
            self.__create_task_for_transcript(video_id)

        if video_from_db and video_from_db.past_update_time(
            int(self.job_data.poll_frequency_in_days)
        ):
            logger.info("Video data stale. Refreshing from API.")
            youtube_response = self.youtube_api.fetch_video_details(video_id)
            latest_youtube_data = YouTubeVideoDBData.to_cls_from_response(
                {**youtube_response, "task_id": str(self.task.id)}
            )
            self.db.update_video(latest_youtube_data.values_to_update(video_from_db))

    def __create_task_for_transcript(self, video_id: str) -> None:
        job = YouTubeVideoSummarizeJobData(
            ref_id=self.job_data.ref_id,
        )
        task = TaskData(
            id=uuid4(),
            job_type=JobEnum.YouTubeVideoSummarize,
            payload=job.to_json(),
            created_by=JobEnum.YouTubeVideo,
            created_at=datetime.now(),
            failed_count=0,
            status=TaskStatusEnum.IN_PROGRESS,
            trail=[self.task.id],
        )
        TaskDB().add_task(task)
        logger.info(
            "Created summarize task for video id: %s with task id: %s",
            video_id,
            task.id,
        )

    def __create_platform_data(self, video_id: str) -> str:
        data = PlatformDBData(
            platform_type=PlatformEnum.YouTubeVideo,
            data=PlatformYouTubeVideoDBData(
                channel_id=self.job_data.platform.channel_id, video_id=video_id
            ),
        )
        logger.info(
            "Saving platform data for video id: %s to database with ref_id: %s",
            video_id,
            self.job_data.ref_id,
        )
        return PlatformDB().save_data(data)
