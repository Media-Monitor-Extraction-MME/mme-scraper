'''
Entry point for testing cases.
'''

#Imports
from General.DB.DataBaseManager import DBManager
from General.scraperservice import ScraperService
from General.Platforms import _Platforms
from General.RepoStructure.commentrepo import CommentRepo
from General.RepoStructure.communityrepo import CommunityRepo
from General.RepoStructure.postrepo import PostRepo

from Scrapers.Reddit.RedditScraperClass import RedditScraper
from Scrapers.Twitter.TwitterScraperClass import TwitterScraper
from Scrapers.Twitter.account_data import *

from playwright.async_api import async_playwright

from unittest.mock import patch
import unittest

import logging
import asyncio

async def main():
    username = None
    password = None

    try:
        with open('Scrapers/Twitter/account_data/accounts.txt', 'r') as file:
            logging.info("File found")
            last_line = file.readlines()[-1]
            account = last_line.split(', ')
            username = account[1].strip()
            password = account[3].strip()
    except FileNotFoundError as fe:
        logging.error(f"File not found: {fe}")    

    twitterscraper = TwitterScraper(link_gather_account_username=username, link_gather_account_password=password)
    redditscraper = RedditScraper
    manager = DBManager(db_name='tests')

    if twitterscraper:
        async with async_playwright() as p:
            browser = await p.chromium.launch(args=['--start-maximized'], headless=False)

            keyword = 'Mbappe'

            page = await twitterscraper.login_account(browser)
            if page is None:
                logging.error("Page is none")
            links = await twitterscraper.link_gatherer(page, keyword)
            data = await twitterscraper.scraper(browser, links)

            await manager.insert_documents("testsamplesTwitter", data)

asyncio.run(main())

