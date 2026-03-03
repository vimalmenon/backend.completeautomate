from backend.data import PlatformDBData
from backend.database.dynamo_database import DbManager


class PlatformDB:
    TABLE = "CA#PLATFORM"

    def __init__(self):
        self.db_manager = DbManager()

    def get_data(self) -> PlatformDBData:
        pass

    def save_data(self, data: PlatformDBData) -> None:
        pass
