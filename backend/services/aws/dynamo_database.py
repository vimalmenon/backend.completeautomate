from botocore.exceptions import ClientError

from backend.config.env import env
from backend.services.aws.session import Session


class DbManager:
    def __init__(self):
        session = Session().get_session()
        self.dynamodb = session.resource("dynamodb", region_name=env.aws_region)
        self.table = self.dynamodb.Table(env.table)

    def add_item(self, item: dict):
        return self.table.put_item(Item=item)

    def remove_item(self, data: dict):
        return self.table.delete_item(Key=data)

    def query_items(self, keys) -> list:
        try:
            return self.table.query(
                Select="ALL_ATTRIBUTES",
                ConsistentRead=True,
                KeyConditionExpression=(keys),
            )["Items"]
        except ClientError:
            return []

    def update_item(self, **data):
        return self.table.update_item(**data)

    def get_item(self, key):
        try:
            value = self.table.get_item(Key=key)
            if "Item" in value:
                return value["Item"]
            return None
        except ClientError:
            return None

    def batch_get_item(self, keys: list[dict]):
        try:
            if not keys:
                # Return an empty response structure when no keys are provided
                return {"Responses": {self.table.name: []}, "UnprocessedKeys": {}}
            return self.dynamodb.batch_get_item(
                RequestItems={self.table.name: {"Keys": keys}}
            )
        except ClientError:
            return None
