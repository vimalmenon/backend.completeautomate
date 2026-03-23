from backend.data import S3Data
from backend.helper import FolderHelper
from backend.integration import S3Storage
from backend.manager.prompt_manager import PromptManager
from backend.manager.youtube_channel_manager import YouTubeChannelManager
from backend.manager.youtube_video_manager import YouTubeVideoManager


class DataManager:

    def upload(self) -> bool:
        return True

    def download(self) -> bool:
        self.__download_prompts()
        self.__download_youtube_channels()
        self.__download_youtube_videos()
        return True

    def __download_prompts(self) -> None:
        prompts = PromptManager().get_prompts()
        prompts_data = [prompt.to_json() for prompt in prompts]
        s3_data = S3Data(
            name="prompt_data.pickle",
            content_type=S3Data.detect_content_type_from_name(
                name="prompt_data.pickle"
            ),
        )
        data = FolderHelper().create_pickle_data(data=prompts_data)
        S3Storage().upload_data(s3_data=s3_data, data=data)
        FolderHelper().create_pickle_file(s3_data.downloaded_path, data=data)

    def __download_youtube_channels(self):
        youtube_channels = YouTubeChannelManager(ref_id="").get_channels()
        youtube_channels_data = [channel.to_json() for channel in youtube_channels]
        s3_data = S3Data(
            name="youtube_channels_data.pickle",
            content_type=S3Data.detect_content_type_from_name(
                name="youtube_channels_data.pickle"
            ),
        )
        data = FolderHelper().create_pickle_data(data=youtube_channels_data)
        S3Storage().upload_data(s3_data=s3_data, data=data)
        FolderHelper().create_pickle_file(s3_data.downloaded_path, data=data)

    def __download_youtube_videos(self):
        youtube_videos = YouTubeVideoManager(ref_id="").get_all_videos()
        youtube_videos_data = [video.to_json() for video in youtube_videos]
        s3_data = S3Data(
            name="youtube_videos_data.pickle",
            content_type=S3Data.detect_content_type_from_name(
                name="youtube_videos_data.pickle"
            ),
        )
        data = FolderHelper().create_pickle_data(data=youtube_videos_data)
        S3Storage().upload_data(s3_data=s3_data, data=data)
        FolderHelper().create_pickle_file(s3_data.downloaded_path, data=data)
