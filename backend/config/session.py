from importlib import import_module
from typing import Any

import boto3
from botocore.exceptions import ClientError

from backend.config.env import env
from backend.enum.db_keys import DbKeysEnum

_moto_mock: Any | None = None
_offline_bootstrapped = False


def _start_moto_mock() -> None:
    global _moto_mock

    if _moto_mock is not None:
        return

    try:
        mock_aws = import_module("moto").mock_aws
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "OFFLINE=true requires moto to be installed. "
            "Install it with: poetry add --group dev moto"
        ) from exc

    _moto_mock = mock_aws()
    _moto_mock.start()


def _create_offline_session() -> boto3.Session:
    return boto3.Session(
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
        region_name=env.AWS_REGION,
    )


def _ensure_offline_s3_bucket(session: boto3.Session) -> None:
    s3_client = session.client("s3", region_name=env.AWS_REGION)
    try:
        s3_client.head_bucket(Bucket=env.AWS_S3_BUCKET)
    except ClientError:
        s3_client.create_bucket(Bucket=env.AWS_S3_BUCKET)


def _create_dynamodb_table(dynamodb) -> None:
    try:
        table = dynamodb.create_table(
            TableName=env.AWS_TABLE,
            KeySchema=[
                {"AttributeName": DbKeysEnum.Primary.value, "KeyType": "HASH"},
                {"AttributeName": DbKeysEnum.Secondary.value, "KeyType": "RANGE"},
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": DbKeysEnum.Primary.value,
                    "AttributeType": "S",
                },
                {
                    "AttributeName": DbKeysEnum.Secondary.value,
                    "AttributeType": "S",
                },
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()
    except ClientError as create_error:
        if _get_error_code(create_error) != "ResourceInUseException":
            raise


def _ensure_offline_dynamodb_table(session: boto3.Session) -> None:
    dynamodb = session.resource("dynamodb", region_name=env.AWS_REGION)
    try:
        dynamodb.meta.client.describe_table(TableName=env.AWS_TABLE)
    except ClientError as error:
        if _get_error_code(error) != "ResourceNotFoundException":
            raise
        _create_dynamodb_table(dynamodb)


def _get_error_code(error: ClientError) -> str | None:
    return error.response.get("Error", {}).get("Code")


def ensure_offline_aws() -> None:
    global _offline_bootstrapped

    _start_moto_mock()

    if _offline_bootstrapped:
        return

    session = _create_offline_session()
    _ensure_offline_s3_bucket(session)
    _ensure_offline_dynamodb_table(session)

    _offline_bootstrapped = True


def set_offline_mode(is_offline: bool) -> None:
    global _moto_mock
    global _offline_bootstrapped

    env.OFFLINE = is_offline

    if is_offline:
        ensure_offline_aws()
        return

    if _moto_mock is not None:
        _moto_mock.stop()
        _moto_mock = None
    _offline_bootstrapped = False


class AWSSession:
    @staticmethod
    def get_static_session():
        if env.OFFLINE:
            ensure_offline_aws()
            return boto3.Session(
                aws_access_key_id="testing",
                aws_secret_access_key="testing",
                region_name=env.AWS_REGION,
            )
        return boto3.Session(
            aws_access_key_id=env.AWS_CLIENT_ID,
            aws_secret_access_key=env.AWS_SECRET,
            region_name=env.AWS_REGION,
        )
