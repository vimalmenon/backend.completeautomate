from backend.config.env import env
from backend.data.s3 import S3Data
from backend.enum import JobEnum, PlatformEnum
from backend.helper.folder_helper.folder_helper import FolderHelper
from backend.integration.storage.s3_storage import S3Storage
from backend.manager.platform_manager import PlatformManager
from backend.manager.task_manager import TaskManager


class StartUpManager:
    def start(self):
        self.__add_start_up_file()
        ref_id = self.__create_ref_id_if_not_exists()
        self.__add_channel_if_not_exists(ref_id)

    def __add_channel_if_not_exists(self, ref_id: str) -> None:
        # TODO this is not comprehensive
        manager = TaskManager()
        tasks = manager.get_all_active_tasks()
        result = [task for task in tasks if task.payload.get("ref_id") == ref_id]

        if len(result) == 0:
            task = manager.create_youtube_channel_task(
                ref_id=f"{PlatformEnum.YouTubeChannel.value}#{env.YOUTUBE_CHANNEL_ID}",
                created_by=JobEnum.OWNER,
            )
            manager.add_task(task)

    def __create_ref_id_if_not_exists(self) -> str:
        platform_manager = PlatformManager()
        ref_id = platform_manager.get_platform_by_channel_id(env.YOUTUBE_CHANNEL_ID)
        if not ref_id:
            data = platform_manager.create_channel_data(env.YOUTUBE_CHANNEL_ID)
            return platform_manager.save_data(data)
        return ref_id

    def __add_start_up_file(self):
        for path in ["pickle/token.pickle", "json/client_secret.json"]:
            data = S3Data.to_cls_from_path(path)
            if not FolderHelper().check_if_file_exists(data.downloaded_path):
                S3Storage().download_data(data)
