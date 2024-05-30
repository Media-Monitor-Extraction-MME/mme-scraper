'''
IScraper is the Scraper Interface
'''

#Imports
from abc import ABC, abstractmethod

class IScraper(ABC):
    @abstractmethod
    def scrape(keyword: str):
        pass
