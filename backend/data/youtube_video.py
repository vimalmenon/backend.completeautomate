from dataclasses import dataclass
from typing import Self


@dataclass
class YouTubeVideoReviewerJobData:
    ref_id: str
    transcript: str

    def to_json(self) -> dict:
        return {"ref_id": self.ref_id, "transcript": self.transcript}

    @classmethod
    def to_cls(cls, data) -> Self:
        return cls(ref_id=data["ref_id"], transcript=data["transcript"])
