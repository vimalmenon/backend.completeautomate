import os


class Env:
    VERSION: str = os.environ["VERSION"]
    COMPANY_NAME: str = os.environ["COMPANY_NAME"]
    DEEPSEEK_API_KEY: str = os.environ["DEEPSEEK_API_KEY"]


env = Env()
