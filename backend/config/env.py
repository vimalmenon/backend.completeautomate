import os
from logging import getLogger

from pydantic import SecretStr

logger = getLogger(__name__)


def _to_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _to_list(value) -> list[str]:
    return value.split(",") or []


class Env:
    VERSION: str = os.environ["VERSION"]
    COMPANY_NAME: str = os.environ["COMPANY_NAME"]
    AWS_CLIENT_ID: str = os.environ["AWS_CLIENT_ID"]
    AWS_SECRET: str = os.environ["AWS_SECRET"]
    AWS_REGION: str = os.environ["AWS_REGION"]
    AWS_SECRET_MANAGER: str = os.environ["AWS_SECRET_MANAGER"]
    AWS_TABLE: str = os.environ["AWS_TABLE"]
    AWS_S3_BUCKET: str = os.environ["AWS_S3_BUCKET"]
    SMTP_USERNAME: str = os.environ["SMTP_USERNAME"]
    SMTP_PASSWORD: SecretStr = SecretStr(os.environ["SMTP_PASSWORD"])
    AWS_OUTPUT = "output"
    GROK_API_KEY: SecretStr = SecretStr(os.environ["GROK_API_KEY"])
    PPLX_API_KEY: SecretStr = SecretStr(os.environ["PPLX_API_KEY"])
    OPEN_ROUTE_API_KEY: SecretStr = SecretStr(os.environ["OPEN_ROUTE_API_KEY"])
    OPENAI_API_KEY: SecretStr = SecretStr(os.environ["OPENAI_API_KEY"])
    QWEN_API_KEY: SecretStr = SecretStr(os.environ["QWEN_API_KEY"])
    DEEPSEEK_API_KEY: SecretStr = SecretStr(os.environ["DEEPSEEK_API_KEY"])
    RESEMBLE_API_KEY: SecretStr = SecretStr(os.environ["RESEMBLE_API_KEY"])
    YOUTUBE_API_KEY: str = os.environ["YOUTUBE_API_KEY"]
    YOUTUBE_CHANNEL_ID: str = os.environ["YOUTUBE_CHANNEL_ID"]
    OFFLINE: bool = _to_bool(os.environ.get("OFFLINE", "false"))
    CORS_ALLOWED_ORIGINS: list[str] = _to_list(os.environ["CORS_ALLOWED_ORIGINS"])
    NOTIFICATION_EMAIL_TO: str = os.environ.get("NOTIFICATION_EMAIL_TO", "")

    # --- Cognito Auth ---
    COGNITO_USER_POOL_ID: str = os.environ.get("COGNITO_USER_POOL_ID", "")
    COGNITO_APP_CLIENT_ID: str = os.environ.get("COGNITO_APP_CLIENT_ID", "")
    COGNITO_REGION: str = os.environ.get("COGNITO_REGION", "us-east-1")
    COGNITO_ADMIN_GROUP_NAME: str = os.environ.get(
        "COGNITO_ADMIN_GROUP_NAME", "admin"
    )
    COGNITO_HOSTED_UI_DOMAIN: str = os.environ.get(
        "COGNITO_HOSTED_UI_DOMAIN", ""
    )


env = Env()


__all__ = ["env"]
