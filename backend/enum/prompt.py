from enum import Enum


class PromptTaskEnum(str, Enum):
    YouTubeThumbnailImageGenerationPrompt = "YouTubeThumbnailImageGenerationPrompt"
    YouTubeVideoSummarization = "YouTubeVideoSummarization"
    YouTubeVideoMetadata = "YouTubeVideoMetadata"
    YouTubeVideoCommunityPost = "YouTubeVideoCommunityPost"
