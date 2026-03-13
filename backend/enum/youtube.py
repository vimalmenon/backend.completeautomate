from enum import Enum


class YouTubeVideoTaskEnum(str, Enum):
    YouTubeVideoStart = "YouTubeVideoStart"
    YouTubeVideoFixTranscript = "YouTubeVideoFixTranscript"
    YouTubeVideoMetadataSelection = "YouTubeVideoMetadataSelection"
    YouTubeVideoThumbnailSelection = "YouTubeVideoThumbnailSelection"
    YouTubeVideoComplete = "YouTubeVideoComplete"


class YouTubeVideoJobStatusEnum(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
