from dataclasses import dataclass
from typing import Any, Callable

from backend.config.env import env
from backend.data import (
    JobData,
    PlatformDBData,
    PromptDBData,
    S3Data,
    YouTubeChannelDBData,
    YouTubeVideoDBData,
)
from backend.helper import FolderHelper
from backend.integration import S3Storage
from backend.manager.job_manager import JobManager
from backend.manager.platform_manager import PlatformManager
from backend.manager.prompt_manager import PromptManager
from backend.manager.youtube_channel_manager import YouTubeChannelManager
from backend.manager.youtube_video_manager import YouTubeVideoManager


@dataclass
class DbData:
    sb_data: S3Data
    unpickle_data: Callable
    get_data: Callable
    pickle_data: Callable


youtube_videos_data = DbData(
    sb_data=S3Data(
        name="youtube_videos_data.pickle",
        content_type=S3Data.detect_content_type_from_name(
            name="youtube_videos_data.pickle"
        ),
    ),
    unpickle_data=lambda self: print(self),
    get_data=lambda self: print(self),
    pickle_data=lambda self: print(self),
)

youtube_channels_data = DbData(
    sb_data=S3Data(
        name="youtube_channels_data.pickle",
        content_type=S3Data.detect_content_type_from_name(
            name="youtube_channels_data.pickle"
        ),
    ),
    unpickle_data=lambda self: print(self),
    get_data=lambda self: print(self),
    pickle_data=lambda self: print(self),
)

s3_db_data: dict[str, S3Data] = {
    "youtube_videos_data": S3Data(
        name="youtube_videos_data.pickle",
        content_type=S3Data.detect_content_type_from_name(
            name="youtube_videos_data.pickle"
        ),
    ),
    "youtube_channels_data": S3Data(
        name="youtube_channels_data.pickle",
        content_type=S3Data.detect_content_type_from_name(
            name="youtube_channels_data.pickle"
        ),
    ),
    "prompt_data": S3Data(
        name="prompt_data.pickle",
        content_type=S3Data.detect_content_type_from_name(name="prompt_data.pickle"),
    ),
    "offline_jobs_data": S3Data(
        name="offline_jobs_data.pickle",
        content_type=S3Data.detect_content_type_from_name(
            name="offline_jobs_data.pickle"
        ),
    ),
    "platform_data": S3Data(
        name="platform_data.pickle",
        content_type=S3Data.detect_content_type_from_name(name="platform_data.pickle"),
    ),
    "client_secret_data": S3Data(
        name="client_secret.json",
        content_type=S3Data.detect_content_type_from_name(name="client_secret.json"),
    ),
    "token_data": S3Data(
        name="token.pickle",
        content_type=S3Data.detect_content_type_from_name(name="token.pickle"),
    ),
}


class DataManager:

    def upload(self) -> None:
        self.__upload_platform()
        self.__upload_the_prompt()
        self.__upload_youtube_channel()
        self.__upload_youtube_videos()
        self.__upload_offline_jobs()
        self.__upload_to_s3()

    def download(self) -> None:
        self.download_data_and_upload_to_s3()
        self.__download_for_s3()

    def download_data_and_upload_to_s3(self) -> None:
        self.__download_platform_and_upload_to_s3()
        self.__download_prompts_and_upload_to_s3()
        self.__download_youtube_channels_and_upload_to_s3()
        self.__download_youtube_videos_and_upload_to_s3()
        self.__download_offline_jobs_and_upload_to_s3()

    def restore_db_from_s3(self) -> None:
        self.download()
        self.upload()

    def start_up_script(self) -> None:
        for data in [s3_db_data["client_secret_data"], s3_db_data["token_data"]]:
            if not FolderHelper().check_if_file_exists(data.downloaded_path):
                S3Storage().download_data(data)

    def __get_db_data(self) -> list[S3Data]:
        return [value for _, value in s3_db_data.items()]

    def __upload_the_prompt(self) -> None:
        s3_data = s3_db_data["prompt_data"]
        prompts = FolderHelper().unpack_pickle_data(path=s3_data.downloaded_path)
        for prompt in prompts:
            PromptManager().add_prompt(data=PromptDBData.to_cls(prompt))

    def __upload_youtube_channel(self) -> None:
        s3_data = s3_db_data["youtube_channels_data"]
        channels = FolderHelper().unpack_pickle_data(path=s3_data.downloaded_path)
        for channel in channels:
            YouTubeChannelManager(ref_id="").add_channel(
                data=YouTubeChannelDBData.to_cls(channel)
            )

    def __upload_platform(self) -> None:
        s3_data = s3_db_data["platform_data"]
        platforms = FolderHelper().unpack_pickle_data(path=s3_data.downloaded_path)
        for platform in platforms:
            PlatformManager().save_data(PlatformDBData.to_cls(platform))

    def __upload_youtube_videos(self) -> None:
        s3_data = s3_db_data["youtube_videos_data"]
        videos = FolderHelper().unpack_pickle_data(path=s3_data.downloaded_path)
        for video in videos:
            data = YouTubeVideoDBData.to_cls(video)
            YouTubeVideoManager(ref_id=data.ref_id).save_data(data=data)

    def __upload_offline_jobs(self) -> None:
        s3_data = s3_db_data["offline_jobs_data"]
        jobs = FolderHelper().unpack_pickle_data(path=s3_data.downloaded_path)
        for job in jobs:
            JobManager().save_job(JobData.to_cls(job))

    def __upload_to_s3(self):
        s3_values = self.__get_s3_values()
        for value in s3_values:
            S3Storage().upload_data(
                s3_data=value, data=FolderHelper().read_file(value.downloaded_path)
            )

    def __download_for_s3(self):
        s3_values = self.__get_s3_values()
        for value in s3_values:
            S3Storage().download_data(value)

    def __get_s3_values(self) -> list[S3Data]:
        db_data = self.__get_db_data()
        return [
            S3Data.to_cls_from_path(
                "images/YouTubeVideo#UCJyldWqfi4eNRIsQW2zhbFA#Vw_ilJWdzK8/ai-automation-guide-curious-2.jpg"
            ),
            S3Data.to_cls_from_path(
                "images/YouTubeVideo#UCJyldWqfi4eNRIsQW2zhbFA#Vw_ilJWdzK8/ai-automation-guide-excited-3.jpg"
            ),
            S3Data.to_cls_from_path(
                "images/YouTubeVideo#UCJyldWqfi4eNRIsQW2zhbFA#Vw_ilJWdzK8/ai-automation-guide-surprise-1.jpg"
            ),
        ] + db_data

    def __download_prompts_and_upload_to_s3(self) -> None:
        prompts = PromptManager().get_prompts()
        prompts_data = [prompt.to_json() for prompt in prompts]
        s3_data = s3_db_data["prompt_data"]
        self.__create_and_upload_pickle_file(s3_data=s3_data, data=prompts_data)

    def __download_youtube_channels_and_upload_to_s3(self):
        youtube_channels = YouTubeChannelManager(ref_id="").get_channels()
        youtube_channels_data = [channel.to_json() for channel in youtube_channels]
        s3_data = s3_db_data["youtube_channels_data"]
        self.__create_and_upload_pickle_file(
            s3_data=s3_data, data=youtube_channels_data
        )

    def __download_platform_and_upload_to_s3(self) -> None:
        s3_data = s3_db_data["platform_data"]
        platforms = PlatformManager().get_all_platforms()
        platforms_data = [platform.to_json() for platform in platforms]
        self.__create_and_upload_pickle_file(s3_data=s3_data, data=platforms_data)

    def __download_youtube_videos_and_upload_to_s3(self):
        youtube_videos = YouTubeVideoManager(ref_id="").get_videos_by_channel(
            channel_id=env.YOUTUBE_CHANNEL_ID
        )
        youtube_videos_data = [video.to_json() for video in youtube_videos]
        s3_data = s3_db_data["youtube_videos_data"]
        self.__create_and_upload_pickle_file(s3_data=s3_data, data=youtube_videos_data)

    def __download_offline_jobs_and_upload_to_s3(self):
        jobs = JobManager().get_all_offline_jobs()
        job_data = [job.to_json() for job in jobs]
        s3_data = s3_db_data["offline_jobs_data"]
        self.__create_and_upload_pickle_file(s3_data=s3_data, data=job_data)

    def __create_and_upload_pickle_file(self, s3_data: S3Data, data: Any):
        pickle_data = FolderHelper().create_pickle_data(data=data)
        S3Storage().upload_data(s3_data=s3_data, data=pickle_data)
        FolderHelper().create_pickle_file(s3_data.downloaded_path, data=data)


class FileSync:
    def __init__(self):
        for (
            key,
            value,
        ) in s3_db_data.items():
            print(value)
