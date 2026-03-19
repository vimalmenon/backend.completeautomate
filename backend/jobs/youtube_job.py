import logging
import traceback
from typing import Type

from backend.enum import JobEnum, TaskStatusEnum
from backend.exception.app_exception import AppException
from backend.generator import (
    YouTubeChannelCreator,
    YouTubeThumbnailUpdater,
    YouTubeTopicSuggester,
    YouTubeVideoReviewer,
    YouTubeVideoSummarizer,
    YoutubeVideoThumbnailImagePromptSuggester,
)
from backend.jobs.base_job import BaseJob

logger = logging.getLogger(__name__)


class YouTubeJob(BaseJob):

    HANDLERS: dict[JobEnum, Type] = {
        JobEnum.YouTubeChannel: YouTubeChannelCreator,
        JobEnum.YouTubeVideoSummarizer: YouTubeVideoSummarizer,
        JobEnum.YouTubeThumbnailUpdater: YouTubeThumbnailUpdater,
        JobEnum.YouTubeTopicSuggester: YouTubeTopicSuggester,
        JobEnum.YouTubeVideoReviewer: YouTubeVideoReviewer,
        JobEnum.YouTubeVideoThumbnailPromptSuggester: YoutubeVideoThumbnailImagePromptSuggester,
    }

    def execute(self) -> tuple[TaskStatusEnum, int]:
        try:
            generator_cls = self.HANDLERS.get(self.task.job_type)
            if generator_cls is None:
                raise AppException(f"Unsupported job type: {self.task.job_type.value}")

            return (generator_cls(self.task).generate(), 0)
        except Exception:
            error_msg = traceback.format_exc()
            logger.error("Error executing YouTube task %s: %s", self.task.id, error_msg)
            return (TaskStatusEnum.FAILED, self.task.failed_count + 1)
