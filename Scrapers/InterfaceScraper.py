'''
IScraper is the Scraper Interface
'''

#Imports
from abc import ABC, abstractmethod

class IScraper(ABC):
    @abstractmethod
    def scrape(frequency, keywords):
        pass
