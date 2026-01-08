import logging

from backend.data import Task
from backend.enum import JobEnum, TaskStatusEnum
from backend.exception.app_exception import AppException
from backend.generator import (
    YouTubeChannelGenerator,
    YouTubeThumbnailUpdater,
    YouTubeVideoAnalyzer,
    YouTubeVideoDetailUpdater,
    YouTubeVideoGenerator,
    YouTubeVideoSummarizeGenerator,
)
from backend.jobs.base_job import BaseJob

logger = logging.getLogger(__name__)


class YouTubeJob(BaseJob):

    def execute(self, task: Task) -> tuple[TaskStatusEnum, int]:
        try:
            if task.job_type == JobEnum.YouTubeThumbnail:
                return (YouTubeThumbnailUpdater(task).generate(), 0)
            if task.job_type == JobEnum.YouTubeChannel:
                return (YouTubeChannelGenerator(task).generate(), 0)
            if task.job_type == JobEnum.YouTubeVideo:
                return (YouTubeVideoGenerator(task).generate(), 0)
            if task.job_type == JobEnum.YouTubeVideoSummarize:
                return (YouTubeVideoSummarizeGenerator(task).generate(), 0)
            if task.job_type == JobEnum.YouTubeVideoAnalyze:
                return (YouTubeVideoAnalyzer(task).generate(), 0)
            if task.job_type == JobEnum.YouTubeVideoDetailUpdater:
                return (YouTubeVideoDetailUpdater(task).generate(), 0)
            raise AppException(f"Unsupported job type: {task.job_type.value}")
        except Exception as e:
            logger.error("Error executing YouTube task %s: %s", task.id, e)
            return (TaskStatusEnum.FAILED, task.failed_count + 1)
