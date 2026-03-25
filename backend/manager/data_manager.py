from backend.config.env import env
from backend.data import PromptDBData, S3Data, YouTubeChannelDBData
from backend.helper import FolderHelper
from backend.integration import S3Storage
from backend.manager.prompt_manager import PromptManager
from backend.manager.youtube_channel_manager import YouTubeChannelManager
from backend.manager.youtube_video_manager import YouTubeVideoManager


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
        return True

    def transform(self) -> bool:
        # Need to add when there is some transform data
        return False

    def __upload_the_prompt(self) -> None:
        s3_data = S3Data(
            name="prompt_data.pickle",
            content_type=S3Data.detect_content_type_from_name(
                name="prompt_data.pickle"
            ),
        )
        prompts_binary = FolderHelper().unpack_pickle_data(path=s3_data.downloaded_path)
        prompts = FolderHelper().binary_to_list_or_dict(binary_data=prompts_binary)
        for prompt in prompts:
            PromptManager().add_prompt(data=PromptDBData.to_cls(prompt))

    def __upload_youtube_channel(self) -> None:
        s3_data = S3Data(
            name="youtube_channels_data.pickle",
            content_type=S3Data.detect_content_type_from_name(
                name="youtube_channels_data.pickle"
            ),
        )
        channel_binary = FolderHelper().unpack_pickle_data(path=s3_data.downloaded_path)
        channel = FolderHelper().binary_to_list_or_dict(binary_data=channel_binary)
        if isinstance(channel, dict):
            YouTubeChannelManager(ref_id="").add_channel(
                data=YouTubeChannelDBData.to_cls(channel)
            )

    def __upload_youtube_videos(self) -> None:
        s3_data = S3Data(
            name="youtube_videos_data.pickle",
            content_type=S3Data.detect_content_type_from_name(
                name="youtube_videos_data.pickle"
            ),
        )
        videos = FolderHelper().unpack_pickle_data(path=s3_data.downloaded_path)
        for video in videos:
            YouTubeVideoManager(ref_id="").save_data(video)

    def __upload_to_s3(self):
        # TODO Need to implement
        pass

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
        self.__create_and_upload_pickle_file(s3_data=s3_data, data=data)

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
        self.__create_and_upload_pickle_file(s3_data=s3_data, data=data)

    def __download_youtube_videos(self):
        youtube_videos = YouTubeVideoManager(ref_id="").get_videos_by_channel(
            channel_id=env.YOUTUBE_CHANNEL_ID
        )
        youtube_videos_data = [video.to_json() for video in youtube_videos]
        s3_data = S3Data(
            name="youtube_videos_data.pickle",
            content_type=S3Data.detect_content_type_from_name(
                name="youtube_videos_data.pickle"
            ),
        )
        data = FolderHelper().create_pickle_data(data=youtube_videos_data)
        self.__create_and_upload_pickle_file(s3_data=s3_data, data=data)

    def __download_for_s3(self):
        # TODO Need to implement
        pass

    def __create_and_upload_pickle_file(self, s3_data: S3Data, data: bytes):
        S3Storage().upload_data(s3_data=s3_data, data=data)
        FolderHelper().create_pickle_file(s3_data.downloaded_path, data=data)
