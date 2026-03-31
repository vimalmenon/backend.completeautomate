from datetime import datetime
from uuid import uuid4

import pytest

from backend.config.env import env
from backend.data import JobData
from backend.enum import JobsStatusEnum, JobTypeEnum
from backend.generator import (
    YouTubeChannelVideoCheckerJob,
)
from backend.integration.youtube.mock_youtube_api import MockYouTubeAPI


@pytest.mark.unit
class TestYouTubeChannelOffline:

    @staticmethod
    def _build_job(job_type: JobTypeEnum) -> JobData:
        return JobData(
            id=uuid4(),
            status=JobsStatusEnum.NEW,
            type=job_type,
            task_data={"ref_id": "test-ref"},
            description="test job",
            created_at=datetime.now(),
        )

    def test_channel_video_checker_job_uses_mock_api_when_offline(self) -> None:
        original_offline = env.OFFLINE
        env.OFFLINE = True

        try:
            job = self._build_job(JobTypeEnum.YouTubeChannelVideoChecker)
            generator = YouTubeChannelVideoCheckerJob(job)
            assert isinstance(generator.youtube_api, MockYouTubeAPI)
        finally:
            env.OFFLINE = original_offline
