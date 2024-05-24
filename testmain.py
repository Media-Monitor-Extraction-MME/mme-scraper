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
from dotenv import load_dotenv
load_dotenv()

from unittest.mock import patch
import unittest

import logging
import asyncio
import numpy as np
import json


async def run_reddit(redditscraper, manager):
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--start-maximized'], headless=False)

        subreddits = await redditscraper.subreddit_scrape(browser)

        posts = await redditscraper.post_scrape(forums=subreddits, browser=browser)

        if posts:
            commentsArrays = await redditscraper.content_scrape(posts=posts, browser=browser)
            if isinstance(commentsArrays, list):
                logging.info("commentsArrays is a list")
                valid_arrays = []
                for i, arr in enumerate(commentsArrays):
                    if isinstance(arr, np.ndarray):
                        logging.info(f"Element {i} is a NumPy array with shape {arr.shape}")
                        valid_arrays.append(arr)
                    else:
                        try:
                            arr = np.array(arr)
                            logging.info(f"Element {i} converted to NumPy array with shape {arr.shape}")
                            valid_arrays.append(arr)
                        except Exception as e:
                            logging.error(f"Element {i} cannot be converted to NumPy array: {e}")
                if len(valid_arrays) == len(commentsArrays):
                    logging.info("All elements in commentsArrays are now NumPy arrays")
                    commentsArrays = valid_arrays
                else:
                    logging.error("Some elements could not be converted to NumPy arrays")
                    return
            else:
                logging.error("commentsArrays is not a list")
        
        try:
            flat_comments = [arr.flatten() for arr in commentsArrays]
            comments = np.concatenate(flat_comments)    
            len_comments = len(comments)
            print(f"Length of comments: {len_comments} Comments: {comments}")

            with open("comments_output.json", "w") as file:
                json.dump(comments.tolist(), file)
            await manager.insert_documents("redditposts", comments)
            logging.info("Succesfully pushed reddit to database")
        
        except Exception as e:
            logging.error(f"Fuck the manager: {e}")
        finally:
            await browser.close()


async def run_twitter(twitterscraper, manager):
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--start-maximized'], headless=False)

        #keyword = 'EuroVision'

        page = await twitterscraper.login_account(browser)
        if page is None:
            logging.error("Page is none")
        links = await twitterscraper.link_gatherer(page)
        twitterdata = await twitterscraper.scraper(browser, links)

        await browser.close()

        if manager:
            await manager.insert_documents("tweets", twitterdata)
            logging.info("Succesfully pushed twitter to database")

async def main():
    username = None
    password = None
    keyword = "Atalanta"

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
    _manager = DBManager(db_name='scraped_data')
    manager = DBManager(db_name='scraped_data')

    #'''
    await asyncio.gather(
        run_twitter(twitterscraper=twitterscraper, manager=_manager),
        run_reddit(redditscraper=redditscraper, manager=manager)
    )
    #'''

    #await asyncio.gather(
    #    twitterscraper.scrape(keyword=keyword),
    #    redditscraper.scrape(keyword=keyword)
    #)

asyncio.run(main())

