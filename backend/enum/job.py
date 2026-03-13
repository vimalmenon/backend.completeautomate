from enum import Enum


class JobEnum(str, Enum):
    YouTubeChannel = "YouTubeChannel"
    YouTubeVideo = "YouTubeVideo"
    YouTubeThumbnailUpdater = "YouTubeThumbnailUpdater"
    YouTubeVideoSummarizer = "YouTubeVideoSummarizer"
    YouTubeVideoMetadataSuggester = "YouTubeVideoMetadataSuggester"
    YouTubeVideoMetadataUpdater = "YouTubeVideoMetadataUpdater"
    YouTubeVideoThumbnailPromptSuggester = "YouTubeVideoThumbnailPromptSuggester"
    YouTubeTopicSuggester = "YouTubeTopicSuggester"
    YouTubeVideoReviewer = "YouTubeVideoReviewer"
    ImageGenerator = "ImageGenerator"
    ImagePrompt = "ImagePrompt"
    PromptSuggester = "PromptSuggester"
    # TODO Need to implement
    TwitterPost = "TwitterPost"


class JobsEnum(str, Enum):
    YouTubeChannel = "YouTubeChannel"
    YouTubeVideoUpload = "YouTubeVideoUpload"
    YouTubeChannelStats = "YouTubeChannelStats"
    YouTubeVideoStats = "YouTubeVideoStats"
    PROMPT_REVIEW = "PROMPT_REVIEW"


class TasksEnum(str, Enum):
    pass
