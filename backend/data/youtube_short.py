from dataclasses import dataclass
from datetime import datetime
from typing import Self


@dataclass
class YouTubeShortDBData:
    ref_id: str
    channel_id: str
    topic: str
    transcript: str
    published_at: datetime

    def to_json(self) -> dict:
        return {
            "ref_id": self.ref_id,
            "topic": self.topic,
            "channel_id": self.channel_id,
            "transcript": self.transcript,
            "published_at": self.published_at.isoformat(),
        }

    @classmethod
    def to_cls(cls, data) -> Self:
        return cls(
            ref_id=data["ref_id"],
            topic=data["topic"],
            channel_id=data["channel_id"],
            transcript=data["transcript"],
            published_at=datetime.fromisoformat(data["published_at"]),
        )
