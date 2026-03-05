from enum import Enum


class JobEnum(str, Enum):
    OWNER = "OWNER"
    YouTubeChannel = "YouTubeChannel"
    YouTubeVideo = "YouTubeVideo"
    YouTubeThumbnailUpdater = "YouTubeThumbnailUpdater"
    YouTubeVideoSummarizer = "YouTubeVideoSummarizer"
    YouTubeVideoMetadataSuggester = "YouTubeVideoMetadataSuggester"
    YouTubeVideoMetadataUpdater = "YouTubeVideoMetadataUpdater"
    YouTubeVideoThumbnailPromptSuggester = "YouTubeVideoThumbnailPromptSuggester"
    ImageGenerator = "ImageGenerator"
    ImagePrompt = "ImagePrompt"
    PromptSuggester = "PromptSuggester"
    # TODO Need to implement
    TwitterPost = "TwitterPost"
    TrendingIdeaSuggester = "TrendingIdeaSuggester"
