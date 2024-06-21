'''
Contains all interfaces for the repo structure
'''

#Imports
from abc import ABC, abstractmethod

class ITaskRepository(ABC):
    @abstractmethod
    def get_tasks(document):
        pass
class ICommentRepository(ABC):
    @abstractmethod
    def add_comment(document):
        pass

    @abstractmethod
    def remove_comment(document):
        pass

    @abstractmethod
    def update_comment(document):
        pass

    @abstractmethod
    def search_comment(document):
        pass


class IPostRepository(ABC):
    @abstractmethod
    def add_post(document):
        pass

    @abstractmethod
    def remove_post(document):
        pass

    @abstractmethod
    def update_post(document):
        pass

    @abstractmethod
    def search_post(document):
        pass
