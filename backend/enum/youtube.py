from enum import Enum


class YouTubeJobEnum(str, Enum):
    YouTubeVideoCreate = "YouTubeVideoCreate"
    YouTubeVideoSummarize = "YouTubeVideoSummarize"
    YouTubeVideoMetadata = "YouTubeVideoMetadata"
    YouTubeVideoThumbnailPrompts = "YouTubeVideoThumbnailPrompts"
    Complete = "Complete"
