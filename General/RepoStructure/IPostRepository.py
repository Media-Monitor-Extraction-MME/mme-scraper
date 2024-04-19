'''
IPostRepository interface
'''

#Imports
from abc import ABC, abstractmethod

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

    @abstractmethod
    def get_post_by_id(document):
        pass

    @abstractmethod
    def get_post_id(document):
        pass