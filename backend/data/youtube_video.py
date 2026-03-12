from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import cached_property
from typing import Any, Self
from uuid import UUID

from backend.data.image import PromptData
from backend.data.platform import PlatformDBData
from backend.enum import JobStatusEnum


@dataclass
class YouTubeVideoReviewerJobData:
    ref_id: str
    transcript: str

    def to_json(self) -> dict:
        return {"ref_id": self.ref_id, "transcript": self.transcript}

    @classmethod
    def to_cls(cls, data) -> Self:
        return cls(ref_id=data["ref_id"], transcript=data["transcript"])

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)


@dataclass
class YouTubeVideoReviewerDBData:
    ref_id: str
    task_id: str
    downsides: list[str]
    upsides: list[str]

    def to_json(self) -> dict:
        return {
            "ref_id": self.ref_id,
            "task_id": self.task_id,
            "downsides": self.downsides,
            "upsides": self.upsides,
        }

    @classmethod
    def to_cls(cls, data) -> Self:
        return cls(
            ref_id=data["ref_id"],
            task_id=data["task_id"],
            downsides=data["downsides"],
            upsides=data["upsides"],
        )

    @cached_property
    def platform(self) -> PlatformDBData:
        from backend.database.platform.platform_database import PlatformDB

        return PlatformDB().get_data(self.ref_id)


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
class YouTubeVideoMetadataData:
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
    transcript: str | None = None
    summarized_transcript: str | None = None
    comment: str | None = None
    metadata_suggestions: list[YouTubeVideoMetadataData] = field(default_factory=list)
    thumbnail_prompt_suggestions: list[PromptData] = field(default_factory=list)

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
            transcript=data.get("transcript"),
            summarized_transcript=data.get("summarized_transcript"),
            last_updated_at=datetime.fromisoformat(data["last_updated_at"]),
            stats=stats,
            task_id=UUID(data["task_id"]),
            comment=data.get("comment"),
            metadata_suggestions=[
                YouTubeVideoMetadataData.to_cls(suggestion)
                for suggestion in data.get("metadata_suggestions", [])
            ],
            thumbnail_prompt_suggestions=[
                PromptData.to_cls(prompt)
                for prompt in data.get("thumbnail_prompt_suggestions", [])
            ],
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
            "transcript": self.transcript,
            "summarized_transcript": self.summarized_transcript,
            "comment": self.comment,
            "metadata_suggestions": [
                suggestion.to_json() for suggestion in self.metadata_suggestions
            ],
            "thumbnail_prompt_suggestions": [
                prompt.to_json() for prompt in self.thumbnail_prompt_suggestions
            ],
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
        if self.comment != result.comment:
            updated_values["comment"] = self.comment
        return updated_values
