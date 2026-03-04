from enum import Enum


class JobEnum(str, Enum):
    DUMMY = "DUMMY"
    YouTubeChannel = "YouTubeChannel"
    YouTubeVideo = "YouTubeVideo"
    YouTubeThumbnail = "YouTubeThumbnail"
    YouTubeVideoSummarizer = "YouTubeVideoSummarizer"
    YouTubeVideoMetadataSuggester = "YouTubeVideoMetadataSuggester"
    YouTubeVideoMetadataUpdater = "YouTubeVideoMetadataUpdater"
    YouTubeVideoThumbnailPromptSuggester = "YouTubeVideoThumbnailPromptSuggester"
    ImageGenerator = "ImageGenerator"
    ImagePrompt = "ImagePrompt"
    PromptSuggester = "PromptSuggester"
