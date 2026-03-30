from abc import ABC, abstractmethod

from backend.data import JobData, JobDataResponse
from backend.exception.app_exception import AppException


class BaseJob(ABC):

    def __init__(self, job: JobData):
        self.job = job

    @abstractmethod
    def execute(self) -> JobDataResponse:
        raise AppException("Subclasses must implement the execute method")
