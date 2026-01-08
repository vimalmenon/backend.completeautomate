import os
import json
from logging import getLogger

from botocore.exceptions import ClientError

logger = getLogger(__name__)


class Env:
    VERSION: str = os.environ["VERSION"]
    COMPANY_NAME: str = os.environ["COMPANY_NAME"]
    AWS_CLIENT_ID: str = os.environ["AWS_CLIENT_ID"]
    AWS_SECRET: str = os.environ["AWS_SECRET"]
    AWS_REGION: str = os.environ["AWS_REGION"]
    AWS_SECRET_MANAGER: str = os.environ["AWS_SECRET_MANAGER"]
    GROQ_API_KEY: str = os.environ["GROQ_API_KEY"]
    ANTHROPIC_API_KEY: str = os.environ["ANTHROPIC_API_KEY"]
    DEEPSEEK_API_KEY: str

    AWS_TABLE: str

    def __init__(self):
        secrets = self.get_from_aws_secret()
        self.DEEPSEEK_API_KEY = str(
            self.__get_from_env_or_secret(secrets, "DEEPSEEK_API_KEY", "")
        )

    def __get_from_env_or_secret(self, secrets: dict[str, str], key: str, default=None):
        """
        Fetches a value from environment variables or AWS Secrets Manager.
        :param key: The key to fetch.
        :return: The value of the key.
        """
        return os.getenv(key, secrets.get(key, default))

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
