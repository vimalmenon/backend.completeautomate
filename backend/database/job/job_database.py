from backend.data import JobData
from backend.database import DbManager
from backend.enum import DbKeysEnum


class JobDB:
    TABLE = "CA#JOB"

    def __init__(self):
        self.db_manager = DbManager()

    def save_data(self, job_data: JobData) -> None:
        self.db_manager.add_item(
            {
                DbKeysEnum.Primary.value: self.TABLE,
                DbKeysEnum.Secondary.value: job_data.id,
                **job_data.to_json(),
            }
        )
