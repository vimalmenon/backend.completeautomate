from enum import Enum


class JobEnum(str, Enum):
    DUMMY = "DUMMY"
    YouTubeChannel = "YouTubeChannel"
    YouTubeVideo = "YouTubeVideo"
    YouTubeThumbnail = "YouTubeThumbnail"
    YouTubeVideoSummarizer = "YouTubeVideoSummarizer"
    YouTubeVideoMetadataSuggester = "YouTubeVideoMetadataSuggester"
    YouTubeVideoMetadataUpdater = "YouTubeVideoMetadataUpdater"
    ImageGenerator = "ImageGenerator"
    ImagePrompt = "ImagePrompt"
    PromptAnalyzer = "PromptAnalyzer"

    # TODO create YouTube Image Generator than Generic one
