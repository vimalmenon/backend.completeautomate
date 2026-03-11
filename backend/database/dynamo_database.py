from typing import Any

from botocore.exceptions import ClientError

from backend.config.env import env
from backend.config.session import get_aws_session


class DbManager:
    def __init__(self):
        session = get_aws_session()
        self.dynamodb = session.resource("dynamodb", region_name=env.AWS_REGION)
        self.table = self.dynamodb.Table(env.AWS_TABLE)

    def add_item(self, item: dict):
        return self.table.put_item(Item=item)

    def remove_item(self, data: dict):
        return self.table.delete_item(Key=data)

    def query_items(
        self,
        keys,
        filter_expression=None,
        expression_attribute_values: dict | None = None,
        expression_attribute_names: dict | None = None,
    ) -> Any:
        try:
            query_args = {
                "Select": "ALL_ATTRIBUTES",
                "ConsistentRead": True,
                "KeyConditionExpression": keys,
            }
            if filter_expression is not None:
                query_args["FilterExpression"] = filter_expression
            if expression_attribute_values is not None:
                query_args["ExpressionAttributeValues"] = expression_attribute_values
            if expression_attribute_names is not None:
                query_args["ExpressionAttributeNames"] = expression_attribute_names
            return self.table.query(**query_args)["Items"]
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

    def get_update_values(self, data: dict) -> tuple[str, dict, dict]:
        update_expression: list[str] = []
        expression_attribute_names = {}
        expression_attribute_values = {}

        for key, value in data.items():
            update_expression.append(f"#{key} = :{key}")
            expression_attribute_names[f"#{key}"] = key
            expression_attribute_values[f":{key}"] = value

        return (
            f"SET {', '.join(update_expression)}",
            expression_attribute_names,
            expression_attribute_values,
        )

    def update_data(self, key: dict, values: dict) -> None:
        update_expression, expression_attribute_names, expression_attribute_values = (
            self.get_update_values(values)
        )
        self.update_item(
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
        )
