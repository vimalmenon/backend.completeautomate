from enum import Enum


class JobEnum(str, Enum):
    DUMMY = "DUMMY"
    YouTubeChannel = "YouTubeChannel"
    YouTubeVideo = "YouTubeVideo"
    YouTubeThumbnail = "YouTubeThumbnail"
    YouTubeVideoSummarize = "YouTubeVideoSummarize"
    YouTubeVideoMetadataSuggester = "YouTubeVideoMetadataSuggester"
    YouTubeVideoMetadataUpdater = "YouTubeVideoMetadataUpdater"
    ImageGenerator = "ImageGenerator"
    ImagePrompt = "ImagePrompt"
    PromptAnalyzer = "PromptAnalyzer"
