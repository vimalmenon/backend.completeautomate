from logging import getLogger

from tabulate import tabulate

from backend.data import S3Data
from backend.helper.folder_helper.folder_helper import FolderHelper
from backend.integration.storage.s3_storage import S3Storage
from backend.manager.job_manager import JobManager
from backend.manager.prompt_manager import PromptManager

logger = getLogger(__name__)


class StartUpManager:
    def start(self) -> None:
        logger.info("Starting startup manager flow")
        self.__add_start_up_file()
        self.__add_start_up_jobs()
        self.__transform_data()
        logger.info("Startup manager flow completed")

    def end(self) -> None:
        self.__sync_prompts()
        self.__show_jobs()

    def __add_start_up_file(self) -> None:
        for path in ["pickle/token.pickle", "json/client_secret.json"]:
            data = S3Data.to_cls_from_path(path)
            if not FolderHelper().check_if_file_exists(data.downloaded_path):
                logger.info(f"Startup file missing locally, downloading: {path}")
                S3Storage().download_data(data)
            else:
                logger.debug(f"Startup file already present: {path}")

    def __add_start_up_jobs(self) -> bool:
        JobManager().create_youtube_channel_onboarding_job()
        return True

    def __transform_data(self) -> bool:
        # Placeholder for any future data transformation logic needed during startup
        return False

    def __sync_prompts(self) -> bool:
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
        return True

    def __show_jobs(self):
        jobs = JobManager().get_all_active_jobs()
        data = [[job.id, job.type, job.status] for job in jobs]
        headers = ["ID", "Type", "Status"]
        print(tabulate(data, headers=headers, tablefmt="grid"))
