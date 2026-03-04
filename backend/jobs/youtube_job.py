import logging

from backend.enum import JobEnum, TaskStatusEnum
from backend.exception.app_exception import AppException
from backend.generator import (
    YouTubeChannelGenerator,
    YouTubeThumbnailUpdater,
    YouTubeVideoDetailUpdater,
    YouTubeVideoGenerator,
    YouTubeVideoMetadataSuggester,
    YouTubeVideoSummarizeGenerator,
)
from backend.jobs.base_job import BaseJob

logger = logging.getLogger(__name__)


class YouTubeJob(BaseJob):

    def execute(self) -> tuple[TaskStatusEnum, int]:
        try:
            if self.task.job_type == JobEnum.YouTubeThumbnail:
                return (YouTubeThumbnailUpdater(self.task).generate(), 0)
            if self.task.job_type == JobEnum.YouTubeChannel:
                return (YouTubeChannelGenerator(self.task).generate(), 0)
            if self.task.job_type == JobEnum.YouTubeVideo:
                return (YouTubeVideoGenerator(self.task).generate(), 0)
            if self.task.job_type == JobEnum.YouTubeVideoSummarize:
                return (YouTubeVideoSummarizeGenerator(self.task).generate(), 0)
            if self.task.job_type == JobEnum.YouTubeVideoMetadataSuggester:
                return (YouTubeVideoMetadataSuggester(self.task).generate(), 0)
            if self.task.job_type == JobEnum.YouTubeVideoMetadataUpdater:
                return (YouTubeVideoDetailUpdater(self.task).generate(), 0)
            raise AppException(f"Unsupported job type: {self.task.job_type.value}")
        except Exception as e:
            logger.error("Error executing YouTube task %s: %s", self.task.id, e)
            return (TaskStatusEnum.FAILED, self.task.failed_count + 1)
