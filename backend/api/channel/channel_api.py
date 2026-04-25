from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException

from backend.data.api import (
    YouTubeChannelResponse,
    YouTubeVideoResponse,
    YouTubeVideoUpdateRequest,
)
from backend.enum import YouTubeVideoStatusEnum, YouTubeVideoTaskEnum
from backend.manager import PlatformManager, YouTubeChannelManager, YouTubeVideoManager

router = APIRouter()
CHANNEL_NOT_FOUND_DETAIL = "Channel not found"
VIDEO_NOT_FOUND_DETAIL = "Video not found"
NOT_FOUND_RESPONSES: dict[int | str, dict[str, Any]] = {
    404: {"description": "Resource not found"}
}


@router.get("/channels", tags=["channels"])
async def list_channels() -> list[YouTubeChannelResponse]:
    channels = YouTubeChannelManager(ref_id="").get_channels()
    return [
        YouTubeChannelResponse.model_validate(channel.to_json()) for channel in channels
    ]


@router.get("/channels/{channel_id}", tags=["channels"], responses=NOT_FOUND_RESPONSES)
async def get_channel(channel_id: str) -> YouTubeChannelResponse:
    platform = PlatformManager().get_platform_by_channel_id(channel_id=channel_id)
    if not platform:
        raise HTTPException(status_code=404, detail=CHANNEL_NOT_FOUND_DETAIL)
    channel = YouTubeChannelManager(ref_id=platform.ref_id).get_channel_details()
    if not channel:
        raise HTTPException(status_code=404, detail=CHANNEL_NOT_FOUND_DETAIL)
    return YouTubeChannelResponse.model_validate(channel.to_json())


@router.get(
    "/channels/{channel_id}/videos",
    tags=["videos"],
)
async def get_videos(channel_id: str) -> list[YouTubeVideoResponse]:
    videos = YouTubeVideoManager(ref_id="").get_videos_by_channel(channel_id=channel_id)
    return [YouTubeVideoResponse.model_validate(video.to_json()) for video in videos]


@router.get(
    "/channels/{channel_id}/videos/{video_id}",
    tags=["videos"],
    responses=NOT_FOUND_RESPONSES,
)
async def get_videos_by_id(channel_id: str, video_id: str) -> YouTubeVideoResponse:
    platform = PlatformManager().get_platform_by_video_id(
        channel_id=channel_id, video_id=video_id
    )
    if not platform:
        raise HTTPException(status_code=404, detail=CHANNEL_NOT_FOUND_DETAIL)
    video = YouTubeVideoManager(ref_id=platform.ref_id).get_video()
    if not video:
        raise HTTPException(status_code=404, detail=VIDEO_NOT_FOUND_DETAIL)
    return YouTubeVideoResponse.model_validate(video.to_json())


@router.put(
    "/channels/{channel_id}/videos/{video_id}",
    tags=["videos"],
    responses=NOT_FOUND_RESPONSES,
)
async def update_video_by_id(
    channel_id: str, video_id: str, data: YouTubeVideoUpdateRequest
) -> YouTubeVideoResponse:
    platform = PlatformManager().get_platform_by_video_id(
        channel_id=channel_id, video_id=video_id
    )
    if not platform:
        raise HTTPException(status_code=404, detail=CHANNEL_NOT_FOUND_DETAIL)

    manager = YouTubeVideoManager(ref_id=platform.ref_id)
    video = manager.get_video()
    if not video:
        raise HTTPException(status_code=404, detail=VIDEO_NOT_FOUND_DETAIL)

    updated_at = datetime.now()
    task_status = YouTubeVideoTaskEnum(data.task_status)
    status = YouTubeVideoStatusEnum(data.status)
    manager.update_video(
        {
            "title": data.title,
            "description": data.description,
            "tags": data.tags,
            "user_message": data.user_message,
            "task_status": task_status,
            "status": status,
            "last_updated_at": updated_at.isoformat(),
        }
    )

    video.title = data.title
    video.description = data.description
    video.tags = data.tags
    video.user_message = data.user_message
    video.task_status = task_status
    video.status = status
    video.last_updated_at = updated_at
    return YouTubeVideoResponse.model_validate(video.to_json())
