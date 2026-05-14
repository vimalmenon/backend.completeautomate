import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from backend.api.channel.channel_api import update_video_by_id
from backend.data import YouTubeVideoDBData
from backend.data.api import YouTubeVideoUpdateRequest
from backend.enum import YouTubeVideoStatusEnum, YouTubeVideoTaskEnum
from backend.manager.youtube_video_manager import YouTubeVideoManager


@pytest.mark.unit
def test_get_videos_by_channel_sorts_by_published_date_desc() -> None:
    newest = YouTubeVideoDBData(
        ref_id="ref-newest",
        channel_id="channel-1",
        video_id="video-newest",
        published_at=datetime.now() + timedelta(days=1),
        last_updated_at=datetime.now(),
        title="Newest",
        description="Newest description",
        thumbnail="https://example.com/newest.jpg",
        tags=[],
        task_status=YouTubeVideoTaskEnum.YouTubeVideoStart,
        language="en",
        stats=[],
    )
    oldest = YouTubeVideoDBData(
        ref_id="ref-oldest",
        channel_id="channel-1",
        video_id="video-oldest",
        published_at=datetime.now() - timedelta(days=1),
        last_updated_at=datetime.now(),
        title="Oldest",
        description="Oldest description",
        thumbnail="https://example.com/oldest.jpg",
        tags=[],
        task_status=YouTubeVideoTaskEnum.YouTubeVideoStart,
        language="en",
        stats=[],
    )
    middle = YouTubeVideoDBData(
        ref_id="ref-middle",
        channel_id="channel-1",
        video_id="video-middle",
        published_at=datetime.now(),
        last_updated_at=datetime.now(),
        title="Middle",
        description="Middle description",
        thumbnail="https://example.com/middle.jpg",
        tags=[],
        task_status=YouTubeVideoTaskEnum.YouTubeVideoStart,
        language="en",
        stats=[],
    )

    with patch(
        "backend.manager.youtube_video_manager.YouTubeVideoDB"
    ) as mock_video_db_cls:
        mock_video_db = mock_video_db_cls.return_value
        mock_video_db.fetch_videos_by_channel.return_value = [middle, oldest, newest]

        videos = YouTubeVideoManager(ref_id="ref-1").get_videos_by_channel(
            channel_id="channel-1"
        )

    assert [video.published_at for video in videos] == [
        newest.published_at,
        middle.published_at,
        oldest.published_at,
    ]


@pytest.mark.unit
def test_update_video_by_id_updates_supported_fields() -> None:
    video = YouTubeVideoDBData(
        ref_id="video-ref-1",
        channel_id="channel-1",
        video_id="video-1",
        published_at=datetime.now(),
        last_updated_at=datetime.now(),
        title="Old title",
        description="Old description",
        thumbnail="https://example.com/thumb.jpg",
        tags=["old-tag"],
        task_status=YouTubeVideoTaskEnum.YouTubeVideoStart,
        language="en",
        stats=[],
    )
    video.user_message = "Old user message"

    with (
        patch(
            "backend.api.channel.channel_api.PlatformManager"
        ) as mock_platform_manager_cls,
        patch(
            "backend.api.channel.channel_api.YouTubeVideoManager"
        ) as mock_video_manager_cls,
    ):
        mock_platform_manager = mock_platform_manager_cls.return_value
        mock_platform_manager.get_platform_by_video_id.return_value = type(
            "PlatformStub", (), {"ref_id": "video-ref-1"}
        )()

        mock_video_manager = mock_video_manager_cls.return_value
        mock_video_manager.get_video.return_value = video

        response = asyncio.run(
            update_video_by_id(
                channel_id="channel-1",
                video_id="video-1",
                data=YouTubeVideoUpdateRequest(
                    title="New title",
                    description="New description",
                    tags=["python", "automation"],
                    user_message="Review this before publishing",
                    task_status=YouTubeVideoTaskEnum.YouTubeVideoComplete,
                    status=YouTubeVideoStatusEnum.Inactive,
                ),
            )
        )

    persisted_values = mock_video_manager.update_video.call_args.args[0]

    assert response.title == "New title"
    assert response.description == "New description"
    assert response.tags == ["python", "automation"]
    assert response.user_message == "Review this before publishing"
    assert response.task_status == YouTubeVideoTaskEnum.YouTubeVideoComplete
    assert response.status == YouTubeVideoStatusEnum.Inactive
    assert persisted_values["title"] == "New title"
    assert persisted_values["status"] == YouTubeVideoStatusEnum.Inactive
    assert persisted_values["task_status"] == YouTubeVideoTaskEnum.YouTubeVideoComplete
    assert "last_updated_at" in persisted_values


@pytest.mark.unit
def test_update_video_by_id_raises_when_platform_missing() -> None:
    with patch(
        "backend.api.channel.channel_api.PlatformManager"
    ) as mock_platform_manager_cls:
        mock_platform_manager = mock_platform_manager_cls.return_value
        mock_platform_manager.get_platform_by_video_id.return_value = None

        with pytest.raises(HTTPException, match="Channel not found"):
            asyncio.run(
                update_video_by_id(
                    channel_id="channel-1",
                    video_id="video-1",
                    data=YouTubeVideoUpdateRequest(
                        title="New title",
                        description="New description",
                        tags=[],
                        task_status=YouTubeVideoTaskEnum.YouTubeVideoStart,
                        status=YouTubeVideoStatusEnum.Active,
                    ),
                )
            )
