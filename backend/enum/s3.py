from enum import Enum


class S3ContentTypeEnum(Enum):
    PNG = "image/png"
    JPEG = "image/jpeg"
    JSON = "application/json"
    PICKLE = "application/octet-stream"
    TXT = "text/plain"
