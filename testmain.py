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
import time

async def run_reddit(redditscraper, manager):
    async with async_playwright() as p:
        start_time = time.time()

        browser = await p.chromium.launch(args=['--start-maximized'], headless=False)

        subreddits = await redditscraper.subreddit_scrape(browser)

        posts = await redditscraper.post_scrape(forums=subreddits, browser=browser)

        if posts:
            comments = await redditscraper.content_scrape(posts=posts, browser=browser)
            
        await manager.insert_documents("redditposts", comments)

        posts_len = len[posts]
        end_time = time.time()
        total_time = end_time - start_time
        print(f'Reddit: {posts_len} posts scraped in {total_time} seconds.')

async def run_twitter(twitterscraper, manager):
    async with async_playwright() as p:
        start_time = time.time()

        browser = await p.chromium.launch(args=['--start-maximized'], headless=False)

        page = await twitterscraper.login_account(browser)
        if page is None:
            logging.error("Page is none")
        links = await twitterscraper.link_gatherer(page)
        twitterdata = await twitterscraper.scraper(browser, links)

        await manager.insert_documents("tweets", twitterdata)

        links_len = len[links]
        end_time = time.time()
        total_time = end_time - start_time
        print(f'Twitter: {links_len} tweets scraped in {total_time} seconds.')

async def main():
    username = None
    password = None
    keyword = "Toni Kroos"

    try:
        with open('Scrapers/Twitter/account_data/accounts.txt', 'r') as file:
            logging.info("File found")
            last_line = file.readlines()[-1]
            account = last_line.split(', ')
            username = account[1].strip()
            password = account[3].strip()
    except FileNotFoundError as fe:
        logging.error(f"File not found: {fe}")    

    twitterscraper = TwitterScraper(link_gather_account_username=username, link_gather_account_password=password, keyword=keyword)
    redditscraper = RedditScraper(query=keyword)
    manager = DBManager(db_name='scraped_data')

    await asyncio.gather(
        run_twitter(twitterscraper=twitterscraper, manager=manager),
        run_reddit(redditscraper=redditscraper, manager=manager)
    )

asyncio.run(main())

