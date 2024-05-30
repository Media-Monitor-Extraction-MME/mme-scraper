'''
Reddit scraper implementation
'''
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
#Imports
#from .ForumEntity import Forum
#from ForumEntity import Forum
#from PostEntity import Post
#from CommentEntity import Comment

from playwright.async_api import async_playwright
from bson import ObjectId
from binascii import hexlify, unhexlify

from InterfaceScraper import IScraper

import re
import asyncio
import datetime
import time

class RedditScraper(IScraper):
    
    #Fields
    #query = str
    keywords = [str]
    keyword = str

    def __init__(self, query):
        self.query = query

    #Methods
    async def subreddit_scrape(self, browser) -> list:
        """
        Scrapes the subreddits related to a query (community search, search query).

        Args:
            @browser: Playwright browser instance.
            @keywords: The keywords to search for

        Returns:
            (list): A list of subreddits related to the query (with more than 2000 subscribers)
        """
        query = self.query.replace(" ", "+")
        
        context = await browser.new_context(no_viewport=True)
        page = await context.new_page() 

        await page.goto("https://old.reddit.com/search/?q="+query+"&type=sr")# go to the reddit search page
        await page.wait_for_load_state('load') 
        
        ## seperate the scraping from loading
        
        subscriber_count_limit = 2000  # limit the subscriber count to 2000
        search_result_selector = 'div[data-fullname]'  # selector for the search results
        subreddit_selector = 'a.search-subreddit-link'  # selector for the subreddit links within a search result
        subscriber_selector = 'span.search-subscribers'  # selector for the subscriber count within a search result

        # Select all search results
        search_results = await page.query_selector_all(search_result_selector)

        filtered_subreddits = []  # filter out the subreddits with less than 2000 subscribers

        # Loop over each search result
        for result in search_results:
            # Select the subreddit link and subscriber count within the current search result
            link_element = await result.query_selector(subreddit_selector)
            count_element = await result.query_selector(subscriber_selector)

            # If the search result doesn't contain a subscriber count, skip it
            if count_element is None:
                continue

            # Get the inner text of the link and count elements
            link = await link_element.inner_text()
            count = await count_element.inner_text()

            # Extract the subscriber count from the count text
            match = re.search(r'(\d+(,\d+)*)', count)
            if match:
                subscribers = int(match.group(1).replace(",", ""))
                if subscribers > subscriber_count_limit:
                    filtered_subreddits.append(link)

        await context.close()
        
        return filtered_subreddits

    async def post_scrape(self, forums, browser) -> dict:
        """
        Scrapes the posts in a subreddit.
        
        Args:
            @forums: the filtered_subreddits gathered.
            @browser: Playwright browser instance
        
        Returns:
            A list of dictionaries containing post data(id,title,source,upvotes,desc,url,time) in the subreddit.
        """
        #Helper Function
        async def map_post(post, attributes):
            mapping = {
                'data-fullname': 'post_id',
                'data-subreddit-prefixed': 'subreddit',
                'data-timestamp': 'timestamp',
                'data-url': 'new_url',
                'data-permalink': 'perma_link',
                'data-score': 'upvotes',
            }
            
            ## check if ad and skips if true
            ## attribute contains this field (data-promoted) so we can check if it's an ad
            ## attributes also contain data-nsfw for nsfw posts
            ## need to get rid of the ugly break -> bad practice
            for attr in attributes:
                if attr['name'] == 'data-promoted' and attr['value'] == 'true':
                    continue
                if attr['name'] in mapping:
                    post[mapping[attr['name']]] = attr['value']
            
            if post['timestamp']:
                timestamp_seconds = int(post['timestamp']) / 1000
                dt = datetime.datetime.fromtimestamp(timestamp_seconds)
                post['timestamp'] = dt
            
            return post
        
        #Helper Function
        async def process_element(page, element):
        
            post = {
                'post_id':None,
                'origin': 'Reddit',
                'subreddit': None,
                'title': '',
                'upvotes': None,
                'description': '',
                'new_url': None,
                'perma_link': None,
                'timestamp': None,
            }
            attributes = await element.evaluate('el => { return Array.from(el.attributes).map(attr => ({name: attr.name, value: attr.value})); }')
            mapped_post = await map_post(post, attributes)
            if mapped_post is not None:
                post.update(mapped_post)
                data_fullname = next(attr['value'] for attr in attributes if attr['name'] == 'data-fullname')
                post['title'] = await (await page.query_selector(f"div[data-fullname='{data_fullname}'] > div.entry.unvoted > div.top-matter > p.title > a" )).inner_text()
                return post
        
        #Initialize every subreddit in batches of 3
        async def launch_contexts(browser, forums):
            contexts = await asyncio.gather(*(browser.new_context() for _ in range(5)))
            for i in range(0, len(forums), 3):
                batch = forums[i:i+3]
                tasks = []
                for j, subreddit in enumerate(batch):
                    context = contexts[j % len(contexts)]
                    page = await context.new_page()
                    tasks.append(load_pages(page, subreddit))
                tasks_results = await asyncio.gather(*tasks)
            return tasks_results[0]
        
        async def load_pages(page, subreddit):
            await page.goto(f"https://old.reddit.com/{subreddit}", wait_until='domcontentloaded')
            await page.wait_for_load_state('load')
            elements = await page.query_selector_all('div[data-fullname]')    
            tasks = [process_element(page, element) for element in elements]
            posts = await asyncio.gather(*tasks)
            return posts   
        
        scraped_posts = await launch_contexts(browser, forums)
        return scraped_posts

    async def content_scrape(self, posts, browser) -> dict:
        """
        Scrapes the content of a Reddit post, specifically the comments.
        
        Args:
            @page: The Playwright page object.
            @url: The URL of the Reddit post.
        
        Returns:
            A dictionary containing the title, upvotes, description, and comments of the Reddit post.
        """
        comments_data = []

        async def process_comments(comments, post_id, level=0):
            # Recursively process comments and generate unique IDs for each comment
            processed_comments = []
            for comment in comments:
                #comment_id = await generate_id(comment['fullname'])
                processed_comment = {
                    #'_id': comment_id,
                    'postID': post_id,
                    #'parentId': parent_id,
                    'comment': comment['comment'],
                    'score':  int(comment['score'].split()[0]) if comment['score'] else 0, # the score we get is a string with the score and the word 'points'
                    'level' : level,
                    'children':[]
                }
                if 'children' in comment and comment['children']:
                    processed_comment['children'] = await process_comments(comment['children'], post_id, level + 1)
                processed_comments.append(processed_comment)
            return processed_comments
        
        async def load_pages(page, post):
            await page.goto(f"https://old.reddit.com/{post['perma_link']}", wait_until='domcontentloaded')
            await page.wait_for_load_state('load')
            comment_data = await page.evaluate("""
                        (function fetchComments() {
                            function getCommentData(commentElement) {
                                var comment = commentElement.querySelector(".usertext")?.innerText;
                                var score = commentElement.querySelector(".score")?.innerText;
                                var fullname = commentElement.getAttribute("data-fullname");
                                var children = Array.from(commentElement.querySelectorAll(":scope > .child > .listing > .comment"))
                                    .map(getCommentData);
                                return {comment, score, fullname, children};
                            }

                            var rootComments = document.querySelectorAll("div.commentarea > .sitetable > .comment");
                            return Array.from(rootComments).map(getCommentData);
                        })()
                    """)

            comments_data = await process_comments(comment_data, post['post_id'])
            #comments = [comment for sublist in comments_data for comment in sublist if comment is not None]

            return comments_data  
            
        async def launch_contexts(browser, posts):
            content_scraper_tasks = []
            contexts = await asyncio.gather(*(browser.new_context() for _ in range(5)))
            for i, post in enumerate(posts):
                context = contexts[i % len(contexts)]
                page = await context.new_page()
                timeout = 60000
                page.set_default_timeout(timeout)
                content_scraper_tasks.append(load_pages(page, post))
    
            comments_data = await asyncio.gather(*content_scraper_tasks)
            comments = [comment for sublist in comments_data for comment in sublist if comment is not None]
            return comments

        comments = await launch_contexts(browser, posts)
                
        return comments
      
    async def scrape(self, keyword):
        async with async_playwright() as p:
            browser = await p.chromium.launch(args=['--start-maximized'], headless=False)

            self.query = keyword
            
            subreddits = await self.subreddit_scrape(browser=browser)
            posts = await self.post_scrape(forums=subreddits, browser=browser)
            if posts:
                comments = await self.content_scrape(posts=posts, browser=browser)
            
            return posts, comments
