from boto3.dynamodb.conditions import Attr, Key

from backend.data import JobData, JobTypeEnum
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

    def query_data_by_type(self, type: JobTypeEnum) -> list[JobData]:
        items = self.db_manager.query_items(
            Key(DbKeysEnum.Primary.value).eq(self.TABLE),
            filter_expression=Attr("type").eq(type.value),
        )
        return [JobData.to_cls(item) for item in items]
