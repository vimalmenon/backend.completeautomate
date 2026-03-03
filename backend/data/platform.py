from dataclasses import dataclass
from typing import Self

from backend.enum import PlatformEnum
from backend.exception.app_exception import AppException


@dataclass
class PlatformYouTubeVideoData:
    channel_id: str
    video_id: str

    def to_json(self) -> dict:
        return {"channel_id": self.channel_id, "video_id": self.video_id}

    @classmethod
    def to_cls(cls, data) -> Self:
        return cls(channel_id=data["channel_id"], video_id=data["video_id"])


@dataclass
class PlatformYouTubeChannelData:
    channel_id: str

    def to_json(self) -> dict:
        return {"channel_id": self.channel_id}

    @classmethod
    def to_cls(cls, data) -> Self:
        return cls(channel_id=data["channel_id"])


@dataclass
class PlatformDBData:
    platform_type: PlatformEnum
    data: PlatformYouTubeVideoData | PlatformYouTubeChannelData

    def to_json(self) -> dict:
        return {"data": self.data.to_json(), "platform_type": self.platform_type.value}

    @classmethod
    def to_cls(cls, data) -> Self:
        if data["platform_type"] == PlatformEnum.YouTubeVideo.value:
            return cls(
                data=PlatformYouTubeVideoData.to_cls(data["data"]),
                platform_type=PlatformEnum(data["platform_type"]),
            )
        if data["platform_type"] == PlatformEnum.YouTubeChannel.value:
            return cls(
                data=PlatformYouTubeChannelData.to_cls(data["data"]),
                platform_type=PlatformEnum(data["platform_type"]),
            )
        else:
            raise AppException("Not a valid class")
