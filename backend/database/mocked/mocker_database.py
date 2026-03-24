from backend.config.env import env
from backend.exception.app_exception import AppException


class MockedDB:
    TABLE = "CA#MOCKED_DATA"

    def __init__(self):
        if not env.OFFLINE:
            raise AppException("Application is not offline")
