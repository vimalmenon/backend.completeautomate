from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import cached_property
from typing import Any, Self
from uuid import UUID

from backend.data.platform import PlatformDBData
from backend.data.s3 import S3Data
from backend.enum.status import TaskStatusEnum

NO_ITEMS_FOUND_ERROR = "No items found with in response"


@dataclass
class YouTubeChannelStatsDBData:
    subscriber_count: int
    view_count: int
    video_count: int
    timestamp: datetime

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            subscriber_count=data.get("subscriber_count", 0),
            view_count=data.get("view_count", 0),
            video_count=data.get("video_count", 0),
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )

    def to_json(self) -> dict:
        return {
            "subscriber_count": self.subscriber_count,
            "view_count": self.view_count,
            "video_count": self.video_count,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def to_cls_from_response(cls, data: dict) -> Self:
        return cls(
            subscriber_count=int(data["subscriberCount"]),
            view_count=int(data["viewCount"]),
            video_count=int(data["videoCount"]),
            timestamp=datetime.now(),
        )


@dataclass
class YouTubeChannelDBData:
    ref_id: str
    title: str
    description: str
    custom_url: str
    published_at: datetime
    last_updated_at: datetime
    country: str
    thumbnail_url: str
    banner_image_url: str
    privacy_status: str
    made_for_kids: bool
    task_id: UUID
    stats: list[YouTubeChannelStatsDBData]

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            ref_id=data["ref_id"],
            title=data["title"],
            description=data["description"],
            custom_url=data["custom_url"],
            published_at=datetime.fromisoformat(data["published_at"]),
            country=data["country"],
            thumbnail_url=data["thumbnail_url"],
            banner_image_url=data["banner_image_url"],
            privacy_status=data["privacy_status"],
            made_for_kids=data.get("made_for_kids", False),
            task_id=UUID(data["task_id"]),
            stats=[YouTubeChannelStatsDBData.to_cls(stat) for stat in data["stats"]],
            last_updated_at=datetime.fromisoformat(data["last_updated_at"]),
        )

    @classmethod
    def to_cls_from_response(cls, channel: dict) -> Self:
        snippet = channel["snippet"]
        branding = channel["brandingSettings"]
        status = channel["status"]
        stat = YouTubeChannelStatsDBData.to_cls_from_response(channel["statistics"])
        return cls(
            ref_id=channel["ref_id"],
            title=snippet["title"],
            description=snippet["description"],
            custom_url=snippet["customUrl"],
            published_at=datetime.fromisoformat(snippet["publishedAt"]),
            country=snippet["country"],
            thumbnail_url=snippet["thumbnails"]["default"]["url"],
            banner_image_url=branding["image"]["bannerExternalUrl"],
            privacy_status=status["privacyStatus"],
            made_for_kids=status.get("madeForKids", False),
            task_id=UUID(channel["task_id"]),
            stats=[stat],
            last_updated_at=datetime.now(),
        )

    def to_json(self) -> dict:
        return {
            "title": self.title,
            "ref_id": self.ref_id,
            "description": self.description,
            "custom_url": self.custom_url,
            "published_at": self.published_at.isoformat(),
            "country": self.country,
            "thumbnail_url": self.thumbnail_url,
            "banner_image_url": self.banner_image_url,
            "privacy_status": self.privacy_status,
            "made_for_kids": self.made_for_kids,
            "task_id": str(self.task_id),
            "stats": [stat.to_json() for stat in self.stats],
            "last_updated_at": self.last_updated_at.isoformat(),
        }

    def values_to_update(self, result: Self) -> dict[str, Any]:
        updated_values: dict[str, Any] = {}
        updated_values["stats"] = [stat.to_json() for stat in self.stats + result.stats]
        updated_values["last_updated_at"] = datetime.now().isoformat()
        if self.title != result.title:
            updated_values["title"] = self.title
        if self.description != result.description:
            updated_values["description"] = self.description
        if self.custom_url != result.custom_url:
            updated_values["custom_url"] = self.custom_url
        if self.country != result.country:
            updated_values["country"] = self.country
        if self.thumbnail_url != result.thumbnail_url:
            updated_values["thumbnail_url"] = self.thumbnail_url
        if self.banner_image_url != result.banner_image_url:
            updated_values["banner_image_url"] = self.banner_image_url
        if self.privacy_status != result.privacy_status:
            updated_values["privacy_status"] = self.privacy_status
        if self.made_for_kids != result.made_for_kids:
            updated_values["made_for_kids"] = self.made_for_kids
        return updated_values

    def past_update_time(self, days: int = 7) -> bool:
        delta = datetime.now() - self.last_updated_at
        return delta >= timedelta(days=days)


@dataclass
class YouTubeThumbnailJobData:
    data: S3Data
    status: TaskStatusEnum
    ref_id: str

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def to_json(self) -> dict:
        return {
            "data": self.data.to_json(),
            "status": self.status.value,
            "ref_id": self.ref_id,
            "name": self.name,
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            data=S3Data.to_cls(data["data"]),
            status=TaskStatusEnum(data["status"]),
            ref_id=data["ref_id"],
        )

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)


@dataclass
class YouTubeJobData:
    ref_id: str
    poll_frequency_in_days: int = 7

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def to_json(self) -> dict:
        return {
            "ref_id": self.ref_id,
            "poll_frequency_in_days": self.poll_frequency_in_days,
            "name": self.name,
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            ref_id=data["ref_id"],
            poll_frequency_in_days=data.get("poll_frequency_in_days", 7),
        )

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)


@dataclass
class YouTubeVideoSummarizeJobData:
    ref_id: str
    is_agent = True

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def to_json(self) -> dict:
        return {
            "ref_id": self.ref_id,
            "is_agent": self.is_agent,
            "name": self.name,
        }

    @classmethod
    def to_cls(cls, data) -> Self:
        return cls(
            ref_id=data["ref_id"],
        )

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)


@dataclass
class YouTubeVideoMetadataJobData:
    task_id: UUID
    ref_id: str
    title: str
    description: str
    tags: list[str]

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            task_id=UUID(data["task_id"]),
            ref_id=data["ref_id"],
            title=data["title"],
            description=data["description"],
            tags=data["tags"],
        )

    def to_json(self) -> dict:
        return {
            "task_id": str(self.task_id),
            "ref_id": self.ref_id,
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
            "name": self.name,
        }

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)


@dataclass
class YouTubeVideoThumbnailPromptSuggesterJobData:
    task_id: UUID
    ref_id: str

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            task_id=UUID(data["task_id"]),
            ref_id=data["ref_id"],
        )

    def to_json(self) -> dict:
        return {
            "task_id": str(self.task_id),
            "ref_id": self.ref_id,
            "name": self.name,
        }

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)
