'''
ScraperService class to interact from frontend with backend scrapers.
'''

#Imports
from Platforms import _Platforms
from General.DB.DataBaseManager import *
from Scrapers.Twitter import *
from playwright.async_api import async_playwright
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class ScraperService():
    def __init__(self) -> None:
        pass
        
    '''
    Fields:
    keywords = list of str
    frequency = use AsyncIOScheduler for this. Idk how it works yet 
    platform = enum _Platforms for platform to scrape
    '''

    keywords = [str]
    frequency = int
    platforms = _Platforms

    '''
    Methods:
    set_frequency = takes frequency from frontend and applies it to scrapers. Takes an int as argument
    set_platform = sets the platform(s) to scrape from. Takes members of Enum platforms as argument
    set_keywords = sets the keyword(s) to look for. Takes list of str as argument
    '''
    def set_frequency(frequency):
        raise NotImplementedError("'set_frequency' is yet to be implemented")

    def set_platform(platform):
        raise NotImplementedError("'set_platform' is yet to be implemented")

    def set_keywords(keywords):
        raise NotImplementedError("'set_keywords' is yet to be implemented")

    def start_scraping():
        #raise NotImplementedError("'start_scraping' is yet to be implemented")
        scheduler = AsyncIOScheduler()
        scheduler.add_job(ScraperService.scraping_logic, 'interval', seconds=3)
        scheduler.start()

        return scheduler
    
    def stop_scraping(scheduler):
        #raise NotImplementedError("'stop_scraping' is yet to be implemented")
        scheduler.s
        blabla = AsyncIOScheduler()
        blabla