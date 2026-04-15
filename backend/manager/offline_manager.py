from backend.config.env import env
from backend.config.session import get_aws_session
from backend.manager.data_manager import DataManager


class OfflineManager:
    def __init__(self):
        self.offline = env.OFFLINE
        self.data_manger = DataManager()

    def start(self) -> None:
        if self.offline:
            get_aws_session()
            self.upload_data_to_s3()

    def upload_data_to_s3(self) -> None:
        pass
