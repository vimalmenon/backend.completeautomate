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
from backend.exception import AppException
from backend.helper import FolderHelper
from backend.integration import S3Storage
from backend.manager.job_manager import JobManager
from backend.manager.platform_manager import PlatformManager
from backend.manager.prompt_manager import PromptManager
from backend.manager.youtube_channel_manager import YouTubeChannelManager
from backend.manager.youtube_video_manager import YouTubeVideoManager


@dataclass
class DbData:
    s3_data: S3Data
    get_data: Callable
    upload_data: Callable
    convert_json_to_cls: Callable


youtube_videos_data = DbData(
    s3_data=S3Data(
        name="youtube_videos_data.pickle",
        content_type=S3Data.detect_content_type_from_name(
            name="youtube_videos_data.pickle"
        ),
    ),
    get_data=lambda: YouTubeVideoManager(ref_id="").get_videos_by_channel(
        channel_id=env.YOUTUBE_CHANNEL_ID
    ),
    upload_data=lambda data: YouTubeVideoManager(ref_id=data["ref_id"]).save_data(
        data=YouTubeVideoDBData.to_cls(data)
    ),
    convert_json_to_cls=lambda youtube_videos: [
        video.to_json() for video in youtube_videos
    ],
)

youtube_channels_data = DbData(
    s3_data=S3Data(
        name="youtube_channels_data.pickle",
        content_type=S3Data.detect_content_type_from_name(
            name="youtube_channels_data.pickle"
        ),
    ),
    get_data=lambda: YouTubeChannelManager(ref_id="").get_channels(),
    upload_data=lambda data: YouTubeChannelManager(ref_id="").add_channel(
        data=YouTubeChannelDBData.to_cls(data)
    ),
    convert_json_to_cls=lambda youtube_channels: [
        channel.to_json() for channel in youtube_channels
    ],
)

prompt_data = DbData(
    s3_data=S3Data(
        name="prompt_data.pickle",
        content_type=S3Data.detect_content_type_from_name(name="prompt_data.pickle"),
    ),
    get_data=lambda: PromptManager().get_prompts(),
    upload_data=lambda prompt: PromptManager().add_prompt(
        data=PromptDBData.to_cls(prompt)
    ),
    convert_json_to_cls=lambda prompts: [prompt.to_json() for prompt in prompts],
)


jobs_data = DbData(
    s3_data=S3Data(
        name="jobs_data.pickle",
        content_type=S3Data.detect_content_type_from_name(name="jobs_data.pickle"),
    ),
    get_data=lambda: JobManager().get_all_jobs(),
    upload_data=lambda job: JobManager().save_job(job_data=JobData.to_cls(job)),
    convert_json_to_cls=lambda jobs: [job.to_json() for job in jobs],
)

platform_data = DbData(
    s3_data=S3Data(
        name="platform_data.pickle",
        content_type=S3Data.detect_content_type_from_name(name="platform_data.pickle"),
    ),
    get_data=lambda: PlatformManager().get_all_platforms(),
    upload_data=lambda platform: PlatformManager().save_data(
        platform=PlatformDBData.to_cls(platform)
    ),
    convert_json_to_cls=lambda platforms: [
        platform.to_json() for platform in platforms
    ],
)

db_data = [
    youtube_videos_data,
    youtube_channels_data,
    prompt_data,
    jobs_data,
    platform_data,
]

s3_file_data: dict[str, S3Data] = {
    "client_secret_data": S3Data(
        name="client_secret.json",
        content_type=S3Data.detect_content_type_from_name(name="client_secret.json"),
    ),
    "token_data": S3Data(
        name="token.pickle",
        content_type=S3Data.detect_content_type_from_name(name="token.pickle"),
    ),
    "image_1": S3Data.to_cls_from_path(
        "images/YouTubeVideo#UCJyldWqfi4eNRIsQW2zhbFA#Vw_ilJWdzK8/ai-automation-guide-curious-2.jpg"
    ),
    "image_2": S3Data.to_cls_from_path(
        "images/YouTubeVideo#UCJyldWqfi4eNRIsQW2zhbFA#Vw_ilJWdzK8/ai-automation-guide-excited-3.jpg"
    ),
    "image_3": S3Data.to_cls_from_path(
        "images/YouTubeVideo#UCJyldWqfi4eNRIsQW2zhbFA#Vw_ilJWdzK8/ai-automation-guide-surprise-1.jpg"
    ),
}


class DataManager:

    def upload(self) -> None:
        for db in db_data:
            values = FolderHelper().unpack_pickle_data(path=db.s3_data.downloaded_path)
            for value in values:
                db.upload_data(value)
        self.__upload_to_s3()

    def download_to_local(self) -> None:
        for db in db_data:
            data = db.get_data()
            self.__download_and_upload_pickle_file_to_s3(
                s3_data=db.s3_data, data=db.convert_json_to_cls(data)
            )
        self.__download_for_s3()

    def restore_from_s3(self) -> None:
        self.download_to_local()
        self.upload()

    def start_up_script(self) -> None:
        for data in [s3_file_data["client_secret_data"], s3_file_data["token_data"]]:
            if not FolderHelper().check_if_file_exists(data.downloaded_path):
                try:
                    S3Storage().download_data(data)
                except AppException:
                    if not env.OFFLINE:
                        raise

    def __upload_to_s3(self):
        s3_values = self.__get_s3_values()
        for value in s3_values:
            S3Storage().upload_data(
                s3_data=value, data=FolderHelper().read_file(value.downloaded_path)
            )

    def __download_for_s3(self):
        s3_values = self.__get_s3_values()
        for value in s3_values:
            try:
                S3Storage().download_data(value)
            except AppException:
                if not env.OFFLINE:
                    raise

    def __get_s3_values(self) -> list[S3Data]:
        return [value for _, value in s3_file_data.items()]

    def __download_and_upload_pickle_file_to_s3(self, s3_data: S3Data, data: Any):
        pickle_data = FolderHelper().create_pickle_data(data=data)
        S3Storage().upload_data(s3_data=s3_data, data=pickle_data)
        FolderHelper().create_pickle_file(s3_data.downloaded_path, data=data)


class FileSync:

    def check(self) -> bool:
        for (
            key,
            value,
        ) in s3_file_data.items():
            if value.downloaded_path:
                return False
            print(value)
        return True
