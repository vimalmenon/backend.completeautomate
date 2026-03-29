from enum import Enum


class JobTypeEnum(str, Enum):
    YouTubeChannelOnboarding = "YouTubeChannelOnboarding"
    YouTubeChannel = "YouTubeChannel"
    YouTubeChannelVideoChecker = "YouTubeChannelVideoChecker"
    YouTubeVideo = "YouTubeVideo"
    PromptImprover = "PromptImprover"
    YouTubeStatsUpdater = "YouTubeStatsUpdater"


# JOB DESCRIPTIONS :
# YouTubeChannel = Check for channel and create in Database and also updated the stats for the channel

# YouTubeChannelVideoChecker = Check for new videos in the channel and create a Job for each new video

# YouTubeVideo = Check for video and update in Database
# YouTubeVideoStatsUpdater = Check the stats for the video and update in Database


# YouTubeChannelVideoChecker will create YouTubeVideo & YouTubeVideoStatsUpdater


class JobsStatusEnum(str, Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    PENDING = "PENDING"
    REVIEW = "REVIEW"
    FAILED = "FAILED"
    CLEAN_UP = "CLEAN_UP"
