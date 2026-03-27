from typing import Any

from backend.config.env import env
from backend.data import PromptDBData, S3Data, YouTubeChannelDBData
from backend.helper import FolderHelper
from backend.integration import S3Storage
from backend.manager.job_manager import JobManager
from backend.manager.prompt_manager import PromptManager
from backend.manager.youtube_channel_manager import YouTubeChannelManager
from backend.manager.youtube_video_manager import YouTubeVideoManager

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
}


class DataManager:

    def upload(self) -> bool:
        self.__upload_the_prompt()
        self.__upload_youtube_channel()
        self.__upload_youtube_videos()
        self.__upload_to_s3()
        return True

    def download(self) -> bool:
        self.__download_prompts()
        self.__download_youtube_channels()
        self.__download_youtube_videos()
        self.__download_for_s3()
        self.__download_offline_jobs()
        return True

    def backup_db(self) -> None:
        db_data = self.__get_db_data()
        for data in db_data:
            pass

    def __get_db_data(self) -> list[S3Data]:
        return [value for _, value in s3_db_data.items()]

    def __upload_the_prompt(self) -> None:
        s3_data = s3_db_data["prompt_data"]
        prompts_binary = FolderHelper().unpack_pickle_data(path=s3_data.downloaded_path)
        prompts = FolderHelper().binary_to_list_or_dict(binary_data=prompts_binary)
        for prompt in prompts:
            PromptManager().add_prompt(data=PromptDBData.to_cls(prompt))

    def __upload_youtube_channel(self) -> None:
        s3_data = s3_db_data["youtube_channels_data"]
        channel_binary = FolderHelper().unpack_pickle_data(path=s3_data.downloaded_path)
        channel = FolderHelper().binary_to_list_or_dict(binary_data=channel_binary)
        if isinstance(channel, dict):
            YouTubeChannelManager(ref_id="").add_channel(
                data=YouTubeChannelDBData.to_cls(channel)
            )

    def __upload_youtube_videos(self) -> None:
        s3_data = s3_db_data["youtube_videos_data"]
        videos = FolderHelper().unpack_pickle_data(path=s3_data.downloaded_path)
        for video in videos:
            YouTubeVideoManager(ref_id="").save_data(video)

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

    def __download_prompts(self) -> None:
        prompts = PromptManager().get_prompts()
        prompts_data = [prompt.to_json() for prompt in prompts]
        s3_data = s3_db_data["prompt_data"]
        self.__create_and_upload_pickle_file(s3_data=s3_data, data=prompts_data)

    def __download_youtube_channels(self):
        youtube_channels = YouTubeChannelManager(ref_id="").get_channels()
        youtube_channels_data = [channel.to_json() for channel in youtube_channels]
        s3_data = s3_db_data["youtube_channels_data"]
        self.__create_and_upload_pickle_file(
            s3_data=s3_data, data=youtube_channels_data
        )

    def __download_youtube_videos(self):
        youtube_videos = YouTubeVideoManager(ref_id="").get_videos_by_channel(
            channel_id=env.YOUTUBE_CHANNEL_ID
        )
        youtube_videos_data = [video.to_json() for video in youtube_videos]
        s3_data = s3_db_data["youtube_videos_data"]
        self.__create_and_upload_pickle_file(s3_data=s3_data, data=youtube_videos_data)

    def __download_offline_jobs(self):
        jobs = JobManager().get_all_active_jobs()
        job_data = [job.to_json() for job in jobs]
        s3_data = s3_db_data["offline_jobs_data"]
        self.__create_and_upload_pickle_file(s3_data=s3_data, data=job_data)

    def __create_and_upload_pickle_file(self, s3_data: S3Data, data: Any):
        pickle_data = FolderHelper().create_pickle_data(data=data)
        S3Storage().upload_data(s3_data=s3_data, data=pickle_data)
        FolderHelper().create_pickle_file(s3_data.downloaded_path, data=data)
