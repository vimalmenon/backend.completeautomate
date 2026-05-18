from enum import Enum


class S3ContentTypeEnum(Enum):
    PNG = "image/png"
    JPEG = "image/jpeg"
    JSON = "application/json"
    PICKLE = "application/octet-stream"
    TXT = "text/plain"
    MP3 = "audio/mpeg"
    WAV = "audio/wav"
    MP4 = "video/mp4"
    OGG = "audio/ogg"
    WEBM = "video/webm"
    M4A = "audio/mp4"
    FLAC = "audio/flac"
    AAC = "audio/aac"
    OPUS = "audio/opus"
    AIFF = "audio/aiff"
    WMA = "audio/x-ms-wma"
