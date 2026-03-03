from abc import ABC, abstractmethod

from backend.data import TaskData
from backend.enum import TaskStatusEnum
from backend.exception.app_exception import AppException


class BaseGenerator(ABC):

    def __init__(self, task: TaskData):
        self.task = task

    @abstractmethod
    def generate(self) -> TaskStatusEnum:
        raise AppException("Subclasses must implement the execute method")
