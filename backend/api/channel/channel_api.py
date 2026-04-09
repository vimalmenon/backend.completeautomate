from fastapi import APIRouter, HTTPException

from backend.data.api import YouTubeChannelResponse, YouTubeVideoResponse
from backend.manager import PlatformManager, YouTubeChannelManager, YouTubeVideoManager

router = APIRouter()


@router.get("/channels", tags=["channels"], response_model=list[YouTubeChannelResponse])
async def list_channels() -> list[YouTubeChannelResponse]:
    channels = YouTubeChannelManager(ref_id="").get_channels()
    return [
        YouTubeChannelResponse.model_validate(channel.to_json()) for channel in channels
    ]


@router.get(
    "/channels/{channel_id}", tags=["channels"], response_model=YouTubeChannelResponse
)
async def get_channel(channel_id: str) -> YouTubeChannelResponse:
    platform = PlatformManager().get_platform_by_channel_id(channel_id=channel_id)
    if not platform:
        raise HTTPException(status_code=404, detail="Channel not found")
    channel = YouTubeChannelManager(ref_id=platform.ref_id).get_channel_details()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return YouTubeChannelResponse.model_validate(channel.to_json())


@router.get(
    "/channels/{channel_id}/videos",
    tags=["videos"],
    response_model=list[YouTubeVideoResponse],
)
async def get_videos(channel_id: str) -> list[YouTubeVideoResponse]:
    videos = YouTubeVideoManager(ref_id="").get_videos_by_channel(channel_id=channel_id)
    return [YouTubeVideoResponse.model_validate(video.to_json()) for video in videos]


@router.get(
    "/channels/{channel_id}/videos/{video_id}",
    tags=["videos"],
    response_model=YouTubeVideoResponse,
)
async def get_videos_by_id(channel_id: str, video_id: str) -> YouTubeVideoResponse:
    platform = PlatformManager().get_platform_by_video_id(
        channel_id=channel_id, video_id=video_id
    )
    if not platform:
        raise HTTPException(status_code=404, detail="Channel not found")
    video = YouTubeVideoManager(ref_id=platform.ref_id).get_video()
    return YouTubeVideoResponse.model_validate(video.to_json())
