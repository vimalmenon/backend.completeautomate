from enum import Enum


class S3ContentTypeEnum(Enum):
    PNG = "image/png"
    JPEG = "image/jpeg"
    JSON = "application/json"
    PICKLE = "application/octet-stream"
    TXT = "text/plain"
    MP4 = "video/mp4"
    MP3 = "audio/mpeg"
    WAV = "audio/wav"
    OGG = "audio/ogg"
