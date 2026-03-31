from enum import Enum


class PromptTaskEnum(str, Enum):
    YouTubeThumbnailImageGenerationPrompt = "YouTubeThumbnailImageGenerationPrompt"
    YouTubeVideoSummarization = "YouTubeVideoSummarization"
    YouTubeVideoMetadata = "YouTubeVideoMetadata"
    YouTubeVideoCommunityPost = "YouTubeVideoCommunityPost"


class PromptStatusEnum(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    REVIEW = "REVIEW"
    CLEAN_UP = "CLEAN_UP"
