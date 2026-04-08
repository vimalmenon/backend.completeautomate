from fastapi import APIRouter, HTTPException

from backend.data.api.channel import ChannelData
from backend.manager.youtube_channel_manager import YouTubeChannelManager

router = APIRouter()


@router.get("/channels", tags=["channels"], response_model=list[ChannelData])
def list_channels() -> list[ChannelData]:
    channels = YouTubeChannelManager(ref_id="").get_channels()
    return [ChannelData.model_validate(channel.to_json()) for channel in channels]


@router.get("/channels/{ref_id}", tags=["channels"], response_model=ChannelData)
def get_channel(ref_id: str) -> ChannelData:
    channel = YouTubeChannelManager(ref_id=ref_id).get_channel_details()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    return ChannelData.model_validate(channel.to_json())


@router.get("/channels/{ref_id}/videos", tags=["channels"])
def get_videos(ref_id: str):
    pass


@router.get("/channels/{ref_id}/videos/{video_id}", tags=["channels"])
def get_videos_by_id(ref_id: str, video_id: str):
    pass
