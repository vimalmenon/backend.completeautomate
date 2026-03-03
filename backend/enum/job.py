from enum import Enum


class JobEnum(str, Enum):
    DUMMY = "DUMMY"
    YouTubeChannel = "YouTubeChannel"
    YouTubeVideo = "YouTubeVideo"
    YouTubeThumbnail = "YouTubeThumbnail"
    YouTubeVideoSummarize = "YouTubeVideoSummarize"
    YouTubeVideoAnalyze = "YouTubeVideoAnalyze"  # TODO find Better name
    YouTubeVideoDetailUpdater = "YouTubeVideoDetailUpdater"
    ImageGenerator = "ImageGenerator"
    ImagePrompt = "ImagePrompt"
    PromptAnalyzer = "PromptAnalyzer"
