import os
from logging import getLogger

from pydantic import SecretStr

logger = getLogger(__name__)


class Env:
    VERSION: str = os.environ["VERSION"]
    COMPANY_NAME: str = os.environ["COMPANY_NAME"]
    AWS_CLIENT_ID: str = os.environ["AWS_CLIENT_ID"]
    AWS_SECRET: str = os.environ["AWS_SECRET"]
    AWS_REGION: str = os.environ["AWS_REGION"]
    AWS_SECRET_MANAGER: str = os.environ["AWS_SECRET_MANAGER"]
    AWS_TABLE: str = os.environ["AWS_TABLE"]
    GROQ_API_KEY: SecretStr = SecretStr(os.environ["GROQ_API_KEY"])
    ANTHROPIC_API_KEY: SecretStr = SecretStr(os.environ["ANTHROPIC_API_KEY"])
    PPLX_API_KEY: SecretStr = SecretStr(os.environ["PPLX_API_KEY"])
    OPEN_ROUTE_API_KEY: SecretStr = SecretStr(os.environ["OPEN_ROUTE_API_KEY"])
    OPENAI_API_KEY: SecretStr = SecretStr(os.environ["OPENAI_API_KEY"])
    DEEPSEEK_API_KEY: SecretStr = SecretStr(os.environ["DEEPSEEK_API_KEY"])


env = Env()
