'''
ICommentRepository interface
'''

#Imports
from abc import ABC, abstractmethod

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

    @abstractmethod
    def get_comment_by_id(document):
        pass

    @abstractmethod
    def get_comment_id(document):
        pass