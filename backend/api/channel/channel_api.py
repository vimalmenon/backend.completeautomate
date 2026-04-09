from fastapi import APIRouter, HTTPException

from backend.data.api.channel import ChannelData
from backend.manager import PlatformManager, YouTubeChannelManager, YouTubeVideoManager

router = APIRouter()


@router.get("/channels", tags=["channels"], response_model=list[ChannelData])
def list_channels() -> list[ChannelData]:
    channels = YouTubeChannelManager(ref_id="").get_channels()
    return [ChannelData.model_validate(channel.to_json()) for channel in channels]


@router.get("/channels/{channel_id}", tags=["channels"], response_model=ChannelData)
def get_channel(channel_id: str) -> ChannelData:
    platform = PlatformManager().get_platform_by_channel_id(channel_id=channel_id)
    if not platform:
        raise HTTPException(status_code=404, detail="Channel not found")
    channel = YouTubeChannelManager(ref_id=platform.ref_id).get_channel_details()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return ChannelData.model_validate(channel.to_json())


@router.get("/channels/{channel_id}/videos", tags=["channels"])
def get_videos(channel_id: str):
    return YouTubeVideoManager(ref_id="").get_videos_by_channel(channel_id=channel_id)


@router.get("/channels/{channel_id}/videos/{video_id}", tags=["channels"])
def get_videos_by_id(channel_id: str, video_id: str):
    platform = PlatformManager().get_platform_by_video_id(
        channel_id=channel_id, video_id=video_id
    )
    if not platform:
        raise HTTPException(status_code=404, detail="Channel not found")
    YouTubeVideoManager(ref_id=platform.ref_id).get_video()
