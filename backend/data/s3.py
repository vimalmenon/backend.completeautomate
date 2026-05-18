from dataclasses import dataclass
from typing import Any, Self

from backend.enum.s3 import S3ContentTypeEnum
from backend.exception import AppException


@dataclass
class S3Data:
    name: str
    content_type: S3ContentTypeEnum
    key: str | None = None

    @staticmethod
    def detect_content_type_from_name(name: str) -> S3ContentTypeEnum:
        extension = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        if extension == "png":
            return S3ContentTypeEnum.PNG
        if extension in {"jpg", "jpeg"}:
            return S3ContentTypeEnum.JPEG
        if extension in {"mp3", "wav", "ogg"}:
            if extension == "mp3":
                return S3ContentTypeEnum.MP3
            if extension == "wav":
                return S3ContentTypeEnum.WAV
            return S3ContentTypeEnum.OGG
        if extension == "json":
            return S3ContentTypeEnum.JSON
        if extension == "pickle":
            return S3ContentTypeEnum.PICKLE
        if extension == "mp3":
            return S3ContentTypeEnum.MP3
        if extension == "wav":
            return S3ContentTypeEnum.WAV
        if extension == "mp4":
            return S3ContentTypeEnum.MP4
        if extension == "ogg":
            return S3ContentTypeEnum.OGG
        if extension == "webm":
            return S3ContentTypeEnum.WEBM
        if extension == "m4a":
            return S3ContentTypeEnum.M4A
        if extension == "flac":
            return S3ContentTypeEnum.FLAC
        if extension == "aac":
            return S3ContentTypeEnum.AAC
        if extension == "opus":
            return S3ContentTypeEnum.OPUS
        if extension == "aiff":
            return S3ContentTypeEnum.AIFF
        if extension == "wma":
            return S3ContentTypeEnum.WMA
        raise AppException(
            f"Unsupported file extension for content type detection: {name}"
        )

    def __post_init__(self):
        detected_content_type = self.detect_content_type_from_name(self.name)
        self.content_type = detected_content_type

    def to_json(self) -> dict[str, str | None]:
        return {
            "name": self.name,
            "content_type": self.content_type.value,
            "key": self.key,
            "downloaded_path": self.downloaded_path,
            "s3_key": self.s3_key,
        }

    @classmethod
    def to_cls_from_path(cls, path: str) -> Self:
        parts = path.strip("/").split("/")
        name = parts[-1]

        # Extract key if path has structure: category/key.../name
        # Otherwise key is None (structure: category/name)
        key = "/".join(parts[1:-1]) if len(parts) > 2 else None

        return cls(
            name=name, content_type=cls.detect_content_type_from_name(name), key=key
        )

    @classmethod
    def to_cls(cls, data: dict[str, Any]) -> Self:
        return cls(
            name=data["name"],
            content_type=S3ContentTypeEnum(data["content_type"]),
            key=data.get("key"),
        )

    @property
    def s3_key(self) -> str:  # noqa: C901
        if self.content_type in {
            S3ContentTypeEnum.PNG,
            S3ContentTypeEnum.JPEG,
        }:
            if self.key:
                return f"images/{self.key}/{self.name}"
            return f"images/{self.name}"
        if self.content_type in {
            S3ContentTypeEnum.MP3,
            S3ContentTypeEnum.WAV,
            S3ContentTypeEnum.OGG,
            S3ContentTypeEnum.M4A,
            S3ContentTypeEnum.FLAC,
            S3ContentTypeEnum.AAC,
            S3ContentTypeEnum.OPUS,
            S3ContentTypeEnum.AIFF,
            S3ContentTypeEnum.WMA,
        }:
            if self.key:
                return f"audio/{self.key}/{self.name}"
            return f"audio/{self.name}"
        if self.content_type in {S3ContentTypeEnum.MP4, S3ContentTypeEnum.WEBM}:
            if self.key:
                return f"videos/{self.key}/{self.name}"
            return f"videos/{self.name}"
        if self.content_type == S3ContentTypeEnum.JSON:
            if self.key:
                return f"json/{self.key}/{self.name}"
            return f"json/{self.name}"
        if self.content_type == S3ContentTypeEnum.PICKLE:
            if self.key:
                return f"data/{self.key}/{self.name}"
            return f"data/{self.name}"
        if self.content_type == S3ContentTypeEnum.MP4:
            if self.key:
                return f"videos/{self.key}/{self.name}"
            return f"videos/{self.name}"
        raise AppException("Unsupported content type for S3 key generation")

    @property
    def downloaded_path(self) -> str:  # noqa: C901
        if self.content_type in {
            S3ContentTypeEnum.PNG,
            S3ContentTypeEnum.JPEG,
        }:
            if self.key:
                return f"backend/output/images/{self.key}/{self.name}"
            return f"backend/output/images/{self.name}"
        if self.content_type in {
            S3ContentTypeEnum.MP3,
            S3ContentTypeEnum.WAV,
            S3ContentTypeEnum.OGG,
            S3ContentTypeEnum.M4A,
            S3ContentTypeEnum.FLAC,
            S3ContentTypeEnum.AAC,
            S3ContentTypeEnum.OPUS,
            S3ContentTypeEnum.AIFF,
            S3ContentTypeEnum.WMA,
        }:
            if self.key:
                return f"backend/output/audio/{self.key}/{self.name}"
            return f"backend/output/audio/{self.name}"
        if self.content_type in {S3ContentTypeEnum.MP4, S3ContentTypeEnum.WEBM}:
            if self.key:
                return f"backend/output/video/{self.key}/{self.name}"
            return f"backend/output/video/{self.name}"
        if self.content_type == S3ContentTypeEnum.PICKLE:
            if self.key:
                return f"backend/output/pickle/{self.key}/{self.name}"
            return f"backend/output/pickle/{self.name}"
        raise AppException("Unsupported content type for S3 key generation")
