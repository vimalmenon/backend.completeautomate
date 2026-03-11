from logging import getLogger

from backend.config.env import env
from backend.data import S3Data
from backend.enum import JobEnum, PlatformEnum
from backend.helper.folder_helper.folder_helper import FolderHelper
from backend.integration.storage.s3_storage import S3Storage
from backend.manager import PlatformManager, PromptManager, TaskManager

logger = getLogger(__name__)


class StartUpManager:
    def start(self):
        logger.info("Starting startup manager flow")
        self.__add_start_up_file()
        ref_id = self.__create_ref_id_if_not_exists()
        self.__add_channel_if_not_exists(ref_id)
        self.__transform_data()
        self.__sync_prompts()
        logger.info("Startup manager flow completed")

    def __add_channel_if_not_exists(self, ref_id: str) -> None:
        manager = TaskManager()
        tasks = manager.get_all_active_tasks()
        result = [
            task
            for task in tasks
            if task.payload.get("ref_id") == ref_id
            and task.job_type == JobEnum.YouTubeChannel
        ]

        if len(result) == 0:
            logger.info("No active YouTubeChannel task found, creating bootstrap task")
            task = manager.create_youtube_channel_task(
                ref_id=f"{PlatformEnum.YouTubeChannel.value}#{env.YOUTUBE_CHANNEL_ID}",
            )
            manager.add_task(task)
            logger.info("Bootstrap YouTubeChannel task created and added")
        else:
            logger.debug("Bootstrap YouTubeChannel task already exists")

    def __create_ref_id_if_not_exists(self) -> str:
        platform_manager = PlatformManager()
        ref_id = platform_manager.get_platform_by_channel_id(env.YOUTUBE_CHANNEL_ID)
        if not ref_id:
            logger.info("Platform reference not found, creating new platform record")
            data = platform_manager.create_channel_data(env.YOUTUBE_CHANNEL_ID)
            return platform_manager.save_data(data)
        logger.debug("Using existing platform reference id")
        return ref_id

    def __add_start_up_file(self):
        for path in ["pickle/token.pickle", "json/client_secret.json"]:
            data = S3Data.to_cls_from_path(path)
            if not FolderHelper().check_if_file_exists(data.downloaded_path):
                logger.info(f"Startup file missing locally, downloading: {path}")
                S3Storage().download_data(data)
            else:
                logger.debug(f"Startup file already present: {path}")

    def __transform_data(self) -> bool:
        # Placeholder for any future data transformation logic needed during startup
        return False

    def __sync_prompts(self) -> bool:
        prompts = PromptManager().get_prompts()
        prompts_data = [prompt.to_json() for prompt in prompts]
        print(prompts_data)
        # Placeholder for syncing prompt templates or other necessary data during startup
        return False
