from backend.data import PlatformDBData
from backend.database.dynamo_database import DbManager


class PlatformDB:

    def __init__(self):
        self.db_manager = DbManager()

    def get_data(self) -> PlatformDBData:
        pass
