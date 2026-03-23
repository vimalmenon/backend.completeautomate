from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import cached_property
from typing import Any, Self

from backend.data.image import ImagePromptData
from backend.data.platform import PlatformDBData
from backend.data.s3 import S3Data
from backend.enum import YouTubeVideoTaskEnum


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
    selected: bool = False

    def to_json(self) -> dict:
        return {
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
            "selected": self.selected,
        }

    @classmethod
    def to_cls(cls, data) -> Self:
        return cls(
            title=data["title"],
            description=data["description"],
            tags=data["tags"],
            selected=data.get("selected", False),
        )


@dataclass
class YouTubeVideoReviewData:
    upsides: list[str]
    downsides: list[str]
    overall: str
    rating: int

    def to_json(self) -> dict:
        return {
            "upsides": self.upsides,
            "downsides": self.downsides,
            "overall": self.overall,
            "rating": int(self.rating),
        }

    @classmethod
    def to_cls(cls, data) -> Self:
        return cls(
            upsides=data["upsides"],
            downsides=data["downsides"],
            overall=data["overall"],
            rating=int(data["rating"]),
        )


@dataclass
class YouTubeVideoThumbnailData:
    s3_data: S3Data
    selected: bool = False

    def to_json(self) -> dict:
        return {
            "s3_data": self.s3_data.to_json(),
            "selected": self.selected,
        }

    @classmethod
    def to_cls(cls, data) -> Self:
        return cls(
            s3_data=S3Data.to_cls(data["s3_data"]),
            selected=data.get("selected", False),
        )


@dataclass
class YouTubeVideoDBData:
    ref_id: str
    channel_id: str
    published_at: datetime
    last_updated_at: datetime
    title: str
    description: str
    thumbnail: str
    status: YouTubeVideoTaskEnum
    tags: list[str]
    language: str
    stats: list[YouTubeVideoDBStats]
    transcript: str | None = None
    summarized_transcript: str | None = None
    comment: str | None = None
    metadata_suggestions: list[YouTubeVideoMetadataData] = field(default_factory=list)
    thumbnail_prompt_suggestions: list[ImagePromptData] = field(default_factory=list)
    thumbnails_suggestions: list[YouTubeVideoThumbnailData] = field(
        default_factory=list
    )

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
            channel_id=data["channel_id"],
            description=data["description"],
            thumbnail=data["thumbnail"],
            tags=data["tags"],
            language=data["language"],
            status=data["status"] or YouTubeVideoTaskEnum.YouTubeVideoStart,
            transcript=data.get("transcript"),
            summarized_transcript=data.get("summarized_transcript"),
            last_updated_at=datetime.fromisoformat(data["last_updated_at"]),
            stats=stats,
            comment=data.get("comment"),
            metadata_suggestions=[
                YouTubeVideoMetadataData.to_cls(suggestion)
                for suggestion in data.get("metadata_suggestions", [])
            ],
            thumbnail_prompt_suggestions=[
                ImagePromptData.to_cls(prompt)
                for prompt in data.get("thumbnail_prompt_suggestions", [])
            ],
            thumbnails_suggestions=[
                YouTubeVideoThumbnailData.to_cls(suggestion)
                for suggestion in data.get("thumbnails_suggestions", [])
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
            channel_id=item["channel_id"],
            language=snippet["defaultLanguage"],
            last_updated_at=datetime.now(),
            stats=[stat],
            status=item["status"],
        )

    def to_json(self) -> dict:
        return {
            "ref_id": self.ref_id,
            "title": self.title,
            "description": self.description,
            "published_at": self.published_at.isoformat(),
            "channel_id": self.channel_id,
            "thumbnail": self.thumbnail,
            "tags": self.tags,
            "status": self.status,
            "language": self.language,
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
            "thumbnails_suggestions": [
                suggestion.to_json() for suggestion in self.thumbnails_suggestions
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
