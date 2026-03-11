import logging
import traceback

from backend.enum import JobEnum, TaskStatusEnum
from backend.exception.app_exception import AppException
from backend.generator import (
    YouTubeChannelCreator,
    YouTubeThumbnailUpdater,
    YouTubeTopicSuggester,
    YouTubeVideoCreator,
    YouTubeVideoMetadataSuggester,
    YouTubeVideoMetadataUpdater,
    YouTubeVideoReviewer,
    YouTubeVideoSummarizer,
    YoutubeVideoThumbnailImagePromptSuggester,
)
from backend.jobs.base_job import BaseJob

logger = logging.getLogger(__name__)


class YouTubeJob(BaseJob):

    def execute(self) -> tuple[TaskStatusEnum, int]:
        try:
            if self.task.job_type == JobEnum.YouTubeChannel:
                return (YouTubeChannelCreator(self.task).generate(), 0)
            if self.task.job_type == JobEnum.YouTubeVideo:
                return (YouTubeVideoCreator(self.task).generate(), 0)
            if self.task.job_type == JobEnum.YouTubeVideoSummarizer:
                return (YouTubeVideoSummarizer(self.task).generate(), 0)
            if self.task.job_type == JobEnum.YouTubeThumbnailUpdater:
                return (YouTubeThumbnailUpdater(self.task).generate(), 0)
            if self.task.job_type == JobEnum.YouTubeVideoMetadataSuggester:
                return (YouTubeVideoMetadataSuggester(self.task).generate(), 0)
            if self.task.job_type == JobEnum.YouTubeVideoMetadataUpdater:
                return (YouTubeVideoMetadataUpdater(self.task).generate(), 0)
            if self.task.job_type == JobEnum.YouTubeTopicSuggester:
                return (YouTubeTopicSuggester(self.task).generate(), 0)
            if self.task.job_type == JobEnum.YouTubeVideoReviewer:
                return (YouTubeVideoReviewer(self.task).generate(), 0)
            if self.task.job_type == JobEnum.YouTubeVideoThumbnailPromptSuggester:
                return (
                    YoutubeVideoThumbnailImagePromptSuggester(self.task).generate(),
                    0,
                )
            raise AppException(f"Unsupported job type: {self.task.job_type.value}")
        except Exception:
            error_msg = traceback.format_exc()
            logger.error("Error executing YouTube task %s: %s", self.task.id, error_msg)
            return (TaskStatusEnum.FAILED, self.task.failed_count + 1)
