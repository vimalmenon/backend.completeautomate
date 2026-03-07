import os
from logging import getLogger

from pydantic import SecretStr

logger = getLogger(__name__)


def _to_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Env:
    VERSION: str = os.environ["VERSION"]
    COMPANY_NAME: str = os.environ["COMPANY_NAME"]
    AWS_CLIENT_ID: str = os.environ["AWS_CLIENT_ID"]
    AWS_SECRET: str = os.environ["AWS_SECRET"]
    AWS_REGION: str = os.environ["AWS_REGION"]
    AWS_SECRET_MANAGER: str = os.environ["AWS_SECRET_MANAGER"]
    AWS_TABLE: str = os.environ["AWS_TABLE"]
    AWS_S3_BUCKET: str = os.environ["AWS_S3_BUCKET"]
    AWS_OUTPUT = "output"
    GROK_API_KEY: SecretStr = SecretStr(os.environ["GROK_API_KEY"])
    PPLX_API_KEY: SecretStr = SecretStr(os.environ["PPLX_API_KEY"])
    OPEN_ROUTE_API_KEY: SecretStr = SecretStr(os.environ["OPEN_ROUTE_API_KEY"])
    OPENAI_API_KEY: SecretStr = SecretStr(os.environ["OPENAI_API_KEY"])
    DEEPSEEK_API_KEY: SecretStr = SecretStr(os.environ["DEEPSEEK_API_KEY"])
    YOUTUBE_API_KEY: str = os.environ["YOUTUBE_API_KEY"]
    YOUTUBE_CHANNEL_ID: str = os.environ["YOUTUBE_CHANNEL_ID"]
    OFFLINE: bool = _to_bool(os.environ.get("OFFLINE", "false"))


env = Env()


__all__ = ["env"]
