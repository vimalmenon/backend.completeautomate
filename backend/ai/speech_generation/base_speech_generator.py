from abc import ABC, abstractmethod

from backend.exception.app_exception import AppException


class BaseSpeechGenerator(ABC):

    @abstractmethod
    def generate(self):
        raise AppException("Subclasses must implement the execute method")
