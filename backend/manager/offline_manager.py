from backend.config.env import env
from backend.config.session import AWSSession
from backend.manager.data_manager import DataManager


class OfflineManager:
    def __init__(self):
        self.offline = env.OFFLINE
        self.data_manger = DataManager()

    def start(self) -> None:
        if self.offline:
            AWSSession.get_static_session()
            self.data_manger.upload()
