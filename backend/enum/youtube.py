from enum import Enum


class YouTubeVideoJobEnum(str, Enum):
    YouTubeVideoStart = "YouTubeVideoStart"
    YouTubeVideoFixTranscript = "YouTubeVideoFixTranscript"
    YouTubeVideoMetadataSelection = "YouTubeVideoMetadataSelection"
    YouTubeVideoThumbnailPromptSelection = "YouTubeVideoThumbnailPromptSelection"
    YouTubeVideoReview = "YouTubeVideoReview"
    YouTubeVideoComplete = "YouTubeVideoComplete"


class YouTubeVideoJobStatusEnum(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
