import os
import json
from logging import getLogger

from botocore.exceptions import ClientError

logger = getLogger(__name__)


class Env:
    VERSION: str = os.environ["VERSION"]
    COMPANY_NAME: str = os.environ["COMPANY_NAME"]
    DEEPSEEK_API_KEY: str = os.environ["DEEPSEEK_API_KEY"]

    def __init__(self):
        pass

    def get_from_aws_secret(self) -> dict[str, str]:
        """
        Fetches a secret from AWS Secrets Manager.
        :param key: The key of the secret to fetch.
        :return: The value of the secret.
        """
        import boto3

        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_CLIENT_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET"),
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
        client = session.client("secretsmanager")
        try:
            response = client.get_secret_value(SecretId=os.getenv("AWS_SECRET_MANAGER"))
            return json.loads(response["SecretString"])
        except ClientError:
            return {}
        except Exception:
            logger.error("Unexpected error occurred while fetching AWS secret")
            return {}


env = Env()
