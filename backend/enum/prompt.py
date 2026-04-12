from enum import Enum


class PromptTaskEnum(str, Enum):
    YouTubeThumbnailImageGenerationPrompt = "YouTubeThumbnailImageGenerationPrompt"
    YouTubeVideoSummarization = "YouTubeVideoSummarization"
    YouTubeVideoMetadata = "YouTubeVideoMetadata"
    YouTubeVideoCommunityPost = "YouTubeVideoCommunityPost"
    # TODO need to implement
    YouTubeVideoTwitterPost = "YouTubeVideoTwitterPost"
    YouTubeShortSpeechGenerationPrompt = "YouTubeShortSpeechGenerationPrompt"


class PromptStatusEnum(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    REVIEW = "REVIEW"
    COMPLETE = "COMPLETE"
    CLEAN_UP = "CLEAN_UP"
