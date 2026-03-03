from abc import ABC, abstractmethod

from backend.data import TaskData
from backend.enum.status import TaskStatusEnum
from backend.exception.app_exception import AppException


class BaseJob(ABC):

    def __init__(self, task: TaskData):
        self.task = task

    @abstractmethod
    def execute(self) -> tuple[TaskStatusEnum, int]:
        raise AppException("Subclasses must implement the execute method")
