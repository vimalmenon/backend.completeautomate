from abc import ABC, abstractmethod

from backend.data import JobData
from backend.enum import JobsStatusEnum
from backend.exception.app_exception import AppException


class BaseJob(ABC):

    def __init__(self, job: JobData):
        self.job = job

    @abstractmethod
    def execute(self) -> tuple[JobsStatusEnum, int, dict | None]:
        raise AppException("Subclasses must implement the execute method")
