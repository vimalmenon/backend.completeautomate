from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import cached_property
from typing import Any, Self
from uuid import UUID

from backend.data.platform import PlatformDBData
from backend.data.s3 import S3Data
from backend.enum.status import JobStatusEnum, TaskStatusEnum

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
class YouTubeVideoDBStats:
    views: int
    likes: int
    comments: int
    timestamp: datetime

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            views=data.get("views", 0),
            likes=data.get("likes", 0),
            comments=data.get("comments", 0),
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )

    @classmethod
    def to_cls_from_response(cls, item: dict) -> Self:
        return cls(
            views=int(item["statistics"]["viewCount"]),
            likes=int(item["statistics"]["likeCount"]),
            comments=int(item["statistics"]["commentCount"]),
            timestamp=datetime.now(),
        )

    def to_json(self) -> dict:
        return {
            "views": self.views,
            "likes": self.likes,
            "comments": self.comments,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class YouTubeTranscriptDBData:
    transcript: str
    summarize: str

    def to_json(self):
        return {
            "transcript": self.transcript,
            "summarize": self.summarize,
        }

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        return cls(
            transcript=data["transcript"],
            summarize=data["summarize"],
        )


@dataclass
class YouTubeVideoDBData:
    ref_id: str
    published_at: datetime
    last_updated_at: datetime
    title: str
    description: str
    thumbnail: str
    tags: list[str]
    language: str
    task_id: UUID
    stats: list[YouTubeVideoDBStats]
    transcript: YouTubeTranscriptDBData | None = None

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)

    @classmethod
    def to_cls(cls, data: dict) -> Self:
        stats = [YouTubeVideoDBStats.to_cls(stat) for stat in data["stats"]]
        return cls(
            ref_id=data["ref_id"],
            published_at=datetime.fromisoformat(data["published_at"]),
            title=data["title"],
            description=data["description"],
            thumbnail=data["thumbnail"],
            tags=data["tags"],
            language=data["language"],
            transcript=(
                YouTubeTranscriptDBData.to_cls(data["transcript"])
                if data["transcript"]
                else None
            ),
            last_updated_at=datetime.fromisoformat(data["last_updated_at"]),
            stats=stats,
            task_id=UUID(data["task_id"]),
        )

    @classmethod
    def to_cls_from_response(cls, item: dict) -> Self:
        stat = YouTubeVideoDBStats.to_cls_from_response(item)
        snippet = item["snippet"]
        return cls(
            ref_id=item["ref_id"],
            published_at=datetime.fromisoformat(snippet["publishedAt"]),
            title=snippet["title"],
            description=snippet["description"],
            thumbnail=snippet["thumbnails"].get("default", {}).get("url"),
            tags=snippet.get("tags", []),
            language=snippet["defaultLanguage"],
            last_updated_at=datetime.now(),
            stats=[stat],
            task_id=UUID(item["task_id"]),
        )

    def to_json(self) -> dict:
        return {
            "ref_id": self.ref_id,
            "title": self.title,
            "description": self.description,
            "published_at": self.published_at.isoformat(),
            "thumbnail": self.thumbnail,
            "tags": self.tags,
            "language": self.language,
            "task_id": str(self.task_id),
            "last_updated_at": self.last_updated_at.isoformat(),
            "stats": [stat.to_json() for stat in self.stats],
            "transcript": self.transcript.to_json() if self.transcript else None,
        }

    def past_update_time(self, days: int = 7) -> bool:
        delta = datetime.now() - self.last_updated_at
        return delta >= timedelta(days=days)

    def values_to_update(self, result: Self) -> dict:
        updated_values: dict[str, Any] = {}
        updated_values["stats"] = [stat.to_json() for stat in self.stats + result.stats]
        updated_values["last_updated_at"] = datetime.now().isoformat()
        if self.title != result.title:
            updated_values["title"] = self.title
        if self.description != result.description:
            updated_values["description"] = self.description
        if self.thumbnail != result.thumbnail:
            updated_values["thumbnail"] = self.thumbnail
        if self.tags != result.tags:
            updated_values["tags"] = self.tags
        if self.language != result.language:
            updated_values["language"] = self.language
        return updated_values


@dataclass
class YouTubeThumbnailJobData:
    data: S3Data
    status: TaskStatusEnum
    ref_id: str

    def to_json(self) -> dict:
        return {
            "data": self.data.to_json(),
            "status": self.status.value,
            "ref_id": self.ref_id,
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

    def to_json(self) -> dict:
        return {
            "ref_id": self.ref_id,
            "poll_frequency_in_days": self.poll_frequency_in_days,
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

    def to_json(self) -> dict:
        return {"ref_id": self.ref_id, "is_agent": self.is_agent}

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
class YouTubeVideoDetailDBData:
    title: str
    description: str
    tags: list[str]
    status: JobStatusEnum = JobStatusEnum.NEW

    def to_json(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "tags": self.tags,
        }

    @classmethod
    def to_cls(cls, data) -> Self:
        return cls(
            title=data["title"],
            description=data["description"],
            status=JobStatusEnum(data["status"]),
            tags=data["tags"],
        )


@dataclass
class YouTubeVideoMetadataDBData:
    ref_id: str
    task_id: UUID
    video_details: list[YouTubeVideoDetailDBData]
    comment: str | None = None

    def to_json(self) -> dict:
        return {
            "task_id": str(self.task_id),
            "video_details": [detail.to_json() for detail in self.video_details],
            "comment": self.comment,
            "ref_id": self.ref_id,
        }

    @classmethod
    def to_cls(cls, data) -> Self:
        return cls(
            video_details=[
                YouTubeVideoDetailDBData.to_cls(detail)
                for detail in data["video_details"]
            ],
            comment=data.get("comment"),
            task_id=UUID(data["task_id"]),
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
        }

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)


@dataclass
class YouTubeVideoThumbnailPromptSuggesterJobData:
    task_id: UUID
    ref_id: str

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
        }

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)
