from logging import getLogger

from backend.data import S3Data
from backend.helper.folder_helper.folder_helper import FolderHelper
from backend.integration.storage.s3_storage import S3Storage
from backend.manager.prompt_manager import PromptManager

logger = getLogger(__name__)


class StartUpManager:
    def start(self):
        logger.info("Starting startup manager flow")
        self.__add_start_up_file()
        self.__add_start_up_jobs()
        self.__transform_data()
        self.__sync_prompts()
        logger.info("Startup manager flow completed")

    def __add_start_up_file(self) -> None:
        for path in ["pickle/token.pickle", "json/client_secret.json"]:
            data = S3Data.to_cls_from_path(path)
            if not FolderHelper().check_if_file_exists(data.downloaded_path):
                logger.info(f"Startup file missing locally, downloading: {path}")
                S3Storage().download_data(data)
            else:
                logger.debug(f"Startup file already present: {path}")

    def __add_start_up_jobs(self) -> bool:
        return False

    def __transform_data(self) -> bool:
        # Placeholder for any future data transformation logic needed during startup
        return False

    def __sync_prompts(self) -> bool:
        prompts = PromptManager().get_prompts()
        prompts_data = [prompt.to_json() for prompt in prompts]
        FolderHelper().create_pickle_file(
            path="backend/output/pickle/prompt_data.pickle", data=prompts_data
        )
        return False
