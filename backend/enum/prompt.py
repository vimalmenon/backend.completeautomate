from enum import Enum


class PromptTaskEnum(str, Enum):
    YouTubeThumbnailImageGenerationPrompt = "YouTubeThumbnailImageGenerationPrompt"
    YouTubeVideoSummarization = "YouTubeVideoSummarization"
    YouTubeVideoMetadata = "YouTubeVideoMetadata"
    YouTubeVideoCommunityPost = "YouTubeVideoCommunityPost"
    # TODO need to implement
    YouTubeVideoTwitterPost = "YouTubeVideoTwitterPost"
    YouTubeShortSpeechGenerationPrompt = "YouTubeShortSpeechGenerationPrompt"
    # Blog post generation
    BlogPostGenerationPrompt = "BlogPostGenerationPrompt"
    # Blog topic suggestion from trending data
    BlogTopicSuggestion = "BlogTopicSuggestion"
    # Meta-prompt tasks for the prompt review/evaluation system
    PromptEvaluation = "PromptEvaluation"
    PromptImprovement = "PromptImprovement"


class PromptStatusEnum(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    REVIEW = "REVIEW"
    COMPLETE = "COMPLETE"
    CLEAN_UP = "CLEAN_UP"
