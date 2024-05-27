'''
Entry point for testing cases.
'''

#Imports
from General.DB.DataBaseManager import DBManager
#from General.ScraperService import ScraperService
from General.Platforms import _Platforms
#from General.RepoStructure.CommentRepo import CommentRepo
#from General.RepoStructure.CommunityRepo import CommunityRepo
from General.RepoStructure.PostRepo import PostRepo

from Scrapers.Reddit.RedditScraperClass import RedditScraper
from Scrapers.Twitter.TwitterScraperClass import TwitterScraper
from Scrapers.Twitter.account_data import *

from playwright.async_api import async_playwright

from unittest.mock import patch
import unittest

import logging
import asyncio
import time

async def run_reddit(redditscraper):
    async with async_playwright() as p:
        start_time = time.time()

        browser = await p.chromium.launch(args=['--start-maximized'], headless=False)

        subreddits = await redditscraper.subreddit_scrape(browser)

        posts = await redditscraper.post_scrape(forums=subreddits, browser=browser)

        if posts:
            comments = await redditscraper.content_scrape(posts=posts, browser=browser)
    
        posts_len = len(posts)
        end_time = time.time()
        total_time = end_time - start_time
        print(f'Reddit: {posts_len} posts scraped in {total_time} seconds.')
        
        await browser.close()

        return posts, comments

async def run_twitter(twitterscraper):
    async with async_playwright() as p:
        start_time = time.time()

        browser = await p.chromium.launch(args=['--start-maximized'], headless=False)

        page = await twitterscraper.login_account(browser)
        if page is None:
            logging.error("Page is none")
        links = await twitterscraper.link_gatherer(page)
        twitterdata = await twitterscraper.scraper(browser, links)

        links_len = len(links)
        end_time = time.time()
        total_time = end_time - start_time
        print(f'Twitter: {links_len} tweets scraped in {total_time} seconds.')
        await browser.close()
        
        return twitterdata
    


async def main():
    username = None
    password = None
    keyword = "Rafah"

    try:
        with open('Scrapers/Twitter/account_data/accounts.txt', 'r') as file:
            logging.info("File found")
            last_line = file.readlines()[-1]
            account = last_line.split(', ')
            username = account[1].strip()
            password = account[3].strip()
    except FileNotFoundError as fe:
        logging.error(f"File not found: {fe}")    

    # init scrapers
    twitterscraper = TwitterScraper(link_gather_account_username=username, link_gather_account_password=password, keyword=keyword)
    redditscraper = RedditScraper(query=keyword)

    # scrape the data
    twitter_data, reddit_data = await asyncio.gather(
        run_twitter(twitterscraper=twitterscraper),
        run_reddit(redditscraper=redditscraper)
    )
    
    # upload data
    manager = DBManager(db_name='scraped_data')
    async def insert_documents_in_transaction(session):
        await manager.insert_documents("redditcomments", reddit_data[0], session=session)
        await manager.insert_documents("redditcomments", reddit_data[1], session=session)
        await manager.insert_documents("twitterdata", twitter_data, session=session)
    
    async with await manager.client.start_session() as session:
        result = await session.start_transaction(insert_documents_in_transaction)

asyncio.run(main())

