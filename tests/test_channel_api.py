import asyncio
from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from backend.api.channel.channel_api import update_video_by_id
from backend.data import YouTubeVideoDBData
from backend.data.api import YouTubeVideoUpdateRequest
from backend.enum import YouTubeVideoStatusEnum, YouTubeVideoTaskEnum


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
