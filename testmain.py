'''
Entry point for testing cases.
'''

#Imports
from General.DB.DataBaseManager import DBManager
import json
#from General.ScraperService import ScraperService
from General.Platforms import _Platforms
from General.RepoStructure.Repos import *

from Scrapers.Reddit.RedditScraperClass import RedditScraper
from Scrapers.Twitter.TwitterScraperClass import TwitterScraper
from Scrapers.Twitter.account_data import *

from playwright.async_api import async_playwright
from dotenv import load_dotenv
load_dotenv()

from unittest.mock import patch
import unittest

import logging
import asyncio

import time
import json

# for handler in logging.root.handlers[:]:
#     logging.root.removeHandler(handler)
# logging.basicConfig(filename="logs.log")
# console = logging.StreamHandler()
# console.setLevel(logging.INFO)
# logging.getLogger().addHandler(console)

# logging.info("info")
# logging.warning("warning")

async def run_reddit(redditscraper):
    async with async_playwright() as p:
        start_time = time.time()

        browser = await p.firefox.launch(args=['--start-maximized'])

        subreddits = await redditscraper.subreddit_scrape(browser)

        posts = await redditscraper.post_scrape(forums=subreddits, browser=browser)

        if posts:

            comments = await redditscraper.content_scrape(posts=posts, browser=browser)
    
        posts_len = len(posts)
        comments_len = len(comments)
        end_time = time.time()
        total_time = end_time - start_time
        print(f'Reddit: {posts_len} posts scraped in {total_time} seconds.')
        print(f'RedditL {comments_len} comments scraped in {total_time} seconds.')
        
        await browser.close()

        return posts, comments

async def run_twitter(twitterscraper):
    async with async_playwright() as p:
        start_time = time.time()

        browser = await p.firefox.launch(args=['--start-maximized'])
        print(browser)

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
    # logging.info('Search tasks?')
    manager = DBManager(db_name='scraped_data')
    task_repo = TaskRepo(db=manager, collection="tasks")
    tasks = await task_repo.get_tasks(filter={})
    # logging.info(tasks)
    keywords = []
    for task in tasks:
        keywords.append(task['task']['keyword'])
    logging.info(keywords)
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

    # init scrapers
    twitterscraper = TwitterScraper(link_gather_account_username=username, link_gather_account_password=password, keyword=keyword)
    redditscraper = RedditScraper(query=keyword)

    logging.info("start scraping...")
    #Twitter testing for multiple keywords:
    post_repo = PostRepo(db=manager, collection="posts")
    twitter_tasks = []
    # for keyword in keywords:
    logging.info(f"Keywords: {keywords}")
    twitterscraper = TwitterScraper(username, password, keywords)
    twitter_tasks.append(twitterscraper.scrape(post_repo=post_repo))

    await asyncio.gather(*twitter_tasks)

asyncio.run(main())

