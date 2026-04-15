import boto3
from botocore.exceptions import ClientError

from backend.config.env import env
from backend.enum.db_keys import DbKeysEnum

_moto_mock = None
_offline_bootstrapped = False


def _get_error_code(error: ClientError) -> str | None:
    return error.response.get("Error", {}).get("Code")


def ensure_offline_aws() -> None:
    global _moto_mock
    global _offline_bootstrapped

    if _moto_mock is None:
        try:
            from moto import mock_aws
        except ImportError as exc:
            raise RuntimeError(
                "OFFLINE=true requires moto to be installed. "
                "Install it with: poetry add --group dev moto"
            ) from exc
        _moto_mock = mock_aws()
        _moto_mock.start()

    if _offline_bootstrapped:
        return

    session = boto3.Session(
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
        region_name=env.AWS_REGION,
    )

    s3_client = session.client("s3", region_name=env.AWS_REGION)
    try:
        s3_client.head_bucket(Bucket=env.AWS_S3_BUCKET)
    except ClientError:
        s3_client.create_bucket(Bucket=env.AWS_S3_BUCKET)

    dynamodb = session.resource("dynamodb", region_name=env.AWS_REGION)
    try:
        dynamodb.meta.client.describe_table(TableName=env.AWS_TABLE)
    except ClientError as error:
        if _get_error_code(error) != "ResourceNotFoundException":
            raise

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
