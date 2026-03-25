from enum import Enum


class YouTubeVideoTaskEnum(str, Enum):
    YouTubeVideoStart = "YouTubeVideoStart"
    YouTubeVideoFixTranscript = "YouTubeVideoFixTranscript"
    YouTubeVideoMetadataSelection = "YouTubeVideoMetadataSelection"
    YouTubeVideoThumbnailSelection = "YouTubeVideoThumbnailSelection"
    YouTubeVideoCommunityPost = "YouTubeVideoCommunityPost"
    YouTubeVideoComplete = "YouTubeVideoComplete"


class YouTubeVideoStatusEnum(str, Enum):
    Active = "Active"
    Inactive = "Inactive"
