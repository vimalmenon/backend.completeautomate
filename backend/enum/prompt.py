from enum import Enum


class PromptTaskEnum(str, Enum):
    YouTubeThumbnailImageGenerationPrompt = "YouTubeThumbnailImageGenerationPrompt"
    YouTubeVideoSummarization = "YouTubeVideoSummarization"
    YouTubeVideoAnalysis = "YouTubeVideoAnalysis"
    PromptAnalysis = "PromptAnalysis"
