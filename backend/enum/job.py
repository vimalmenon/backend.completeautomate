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


class JobTypeEnum(str, Enum):
    AddYouTubeChannel = "AddYouTubeChannel"
    AddYouTubeVideo = "AddYouTubeVideo"
    YouTubeVideoChecker = "YouTubeVideoChecker"
    YouTubeChannelStatsUpdater = "YouTubeChannelStatsUpdater"
    YouTubeVideoStatsUpdater = "YouTubeVideoStatsUpdater"


class JobsStatusEnum(str, Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    PENDING = "PENDING"
    REVIEW = "REVIEW"
    FAILED = "FAILED"
