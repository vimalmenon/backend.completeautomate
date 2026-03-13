from enum import Enum


class YouTubeJobEnum(str, Enum):
    YouTubeVideoStart = "YouTubeVideoStart"
    YouTubeFixTranscript = "\YouTubeFixTranscript"
    YouTubeVideoMetadataSelection = "YouTubeVideoMetadataSelection"
    YouTubeVideoThumbnailPromptSelection = "YouTubeVideoThumbnailPromptSelection"
    YouTubeVideoReview = "YouTubeVideoReview"
    YouTubeVideoJobComplete = "YouTubeVideoJobComplete"
