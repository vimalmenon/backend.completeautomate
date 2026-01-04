import os


class Env:
    VERSION: str = os.environ["VERSION"]
    COMPANY_NAME: str = os.environ["COMPANY_NAME"]


env = Env()
