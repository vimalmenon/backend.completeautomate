from abc import ABC, abstractmethod

from backend.data import JobData, TaskData
from backend.enum import JobsStatusEnum, TaskStatusEnum
from backend.exception.app_exception import AppException


class BaseGenerator(ABC):

    def __init__(self, task: TaskData):
        self.task = task

    @abstractmethod
    def generate(self) -> TaskStatusEnum:
        raise AppException("Subclasses must implement the execute method")


class BaseGeneratorJob(ABC):

    def __init__(self, job: JobData):
        self.job = job

    @abstractmethod
    def generate(self) -> JobsStatusEnum:
        raise AppException("Subclasses must implement the execute method")
