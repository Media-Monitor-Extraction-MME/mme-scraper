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
                dt = datetime.date.fromtimestamp(timestamp_seconds)
                post['timestamp'] = dt
            
            return post
        
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
        posts = []
        context = await browser.new_context()

        for subreddit in forums:
            page = await context.new_page()
            await page.goto("https://old.reddit.com/"+subreddit, wait_until='domcontentloaded')
            await page.wait_for_load_state('load')

            id_selector = 'div[data-fullname]'
            elements = await page.query_selector_all(id_selector)
            tasks = [process_element(page, element) for element in elements]
            posts = await asyncio.gather(*tasks)

            return posts
        

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
        
        context = await browser.new_context()

        for post in posts:
            page = await context.new_page()
            url = f"https://old.reddit.com/{post['perma_link']}"
            try:
                await page.goto(url, wait_until='domcontentloaded')
                #await asyncio.sleep(0.3)
            except Exception as e:
                print(f"Error: {e}")
                return {}
            
            # absolute abomination of JS eval
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
            comment_data = await process_comments(comment_data, post['post_id'])
            comments_data.append(comment_data)
                
        return comments_data
    
    async def scrape(self, frequency, keywords):
        ...
    

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--start-maximized'], headless=False)
        scraper = RedditScraper(query="Justin Bieber")

        start_time = time.time()

        subreddits = await scraper.subreddit_scrape(browser)
        print("Subreddits:", subreddits)

        posts = await scraper.post_scrape(forums=subreddits, browser=browser)
        print("Posts:", posts)

        if posts:
            comments = await scraper.content_scrape(posts=posts, browser=browser)
            print("Comments:", comments)

        await browser.close()

        end_time = time.time()
        execution_time = end_time - start_time
        posts_length = len[posts]
        print(f'Execution time: {execution_time} seconds for {posts_length} posts')

if __name__ == "__main__":
    asyncio.run(main())