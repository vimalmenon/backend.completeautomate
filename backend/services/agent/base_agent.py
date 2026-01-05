from abc import ABC, abstractmethod


class BaseAgent(ABC):

    @abstractmethod
    def start_task(self, task: str):
        pass

    @abstractmethod
    def resume_task(self, task_id: str):
        pass
