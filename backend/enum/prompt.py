from enum import Enum


class PromptTaskEnum(str, Enum):
    YouTubeThumbnailImageGenerationPrompt = "YouTubeThumbnailImageGenerationPrompt"
    YouTubeVideoSummarization = "YouTubeVideoSummarization"
    YouTubeVideoAnalysis = "YouTubeVideoAnalysis"
    YouTubeVideoReview = "YouTubeVideoReview"
    PromptAnalysis = "PromptAnalysis"
