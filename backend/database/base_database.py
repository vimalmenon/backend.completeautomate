from abc import ABC, abstractmethod


class BaseDatabase(ABC):

    @abstractmethod
    def get_item(self):
        pass

    @abstractmethod
    def save_item(self, item):
        pass

    @abstractmethod
    def delete_item(self, key):
        pass

    @abstractmethod
    def query_items(self, item):
        pass

    @abstractmethod
    def update_item(self, values):
        pass
