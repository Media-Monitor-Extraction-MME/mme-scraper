'''
ICommunityRepository interface
'''

#Imports
from abc import ABC, abstractmethod

class ICommunityRepository(ABC):
    @abstractmethod
    def add_community(document):
        pass

    @abstractmethod
    def remove_community(document):
        pass

    @abstractmethod
    def update_community(document):
        pass

    @abstractmethod
    def search_community(document):
        pass

    @abstractmethod
    def get_community_by_id(document):
        pass

    @abstractmethod
    def get_community_id(document):
        pass