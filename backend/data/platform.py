from dataclasses import dataclass
from typing import Self, Union

from backend.enum import PlatformEnum
from backend.exception.app_exception import AppException


@dataclass
class PlatformYouTubeVideoDBData:
    channel_id: str
    video_id: str

    def to_json(self) -> dict:
        return {"channel_id": self.channel_id, "video_id": self.video_id}

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        if "channel_id" not in data or "video_id" not in data:
            raise AppException(
                "Missing required fields: channel_id and video_id are required"
            )
        return cls(channel_id=data["channel_id"], video_id=data["video_id"])


@dataclass
class PlatformYouTubeChannelDBData:
    channel_id: str

    def to_json(self) -> dict:
        return {"channel_id": self.channel_id}

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        if "channel_id" not in data:
            raise AppException("Missing required field: channel_id")
        return cls(channel_id=data["channel_id"])


@dataclass
class PlatformDBData:
    platform_type: PlatformEnum
    data: Union[PlatformYouTubeVideoDBData, PlatformYouTubeChannelDBData]

    def to_json(self) -> dict:
        return {"data": self.data.to_json(), "platform_type": self.platform_type.value}

    @property
    def video_id(self) -> str:
        if isinstance(self.data, PlatformYouTubeVideoDBData):
            return self.data.video_id
        raise AppException("Invalid data type for video_id")

    @property
    def channel_id(self) -> str:
        if isinstance(self.data, PlatformYouTubeVideoDBData):
            return self.data.channel_id
        if isinstance(self.data, PlatformYouTubeChannelDBData):
            return self.data.channel_id
        raise AppException("Invalid data type for channel_id")

    @classmethod
    def to_cls(cls, data) -> Self:
        if data["platform_type"] == PlatformEnum.YouTubeVideo.value:
            return cls(
                data=PlatformYouTubeVideoDBData.to_cls(data["data"]),
                platform_type=PlatformEnum(data["platform_type"]),
            )
        if data["platform_type"] == PlatformEnum.YouTubeChannel.value:
            return cls(
                data=PlatformYouTubeChannelDBData.to_cls(data["data"]),
                platform_type=PlatformEnum(data["platform_type"]),
            )
        else:
            raise AppException("Not a valid class")
