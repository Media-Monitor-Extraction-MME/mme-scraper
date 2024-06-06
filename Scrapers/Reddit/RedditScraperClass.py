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
import hashlib

import hashlib


from InterfaceScraper import IScraper

import re
import asyncio
import datetime



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

    async def generate_id(self, string: str) -> str:
        """
        Generates a unique ID from a string.
        
        Args:
            @string: The string to generate an ID from.
        
        Returns:
            (str): The generated ID.
        """
        # Hash the input string using SHA-1
        hash_object = hashlib.sha1(string.encode())
        
        # Take the first 12 bytes of the hash
        objectid_hex = hash_object.hexdigest()[:24]
        
        # Create an ObjectId from the hex string
        object_id = ObjectId(objectid_hex)
        
        return object_id
    

    async def generate_id(self, string: str) -> str:
        """
        Generates a unique ID from a string.
        
        Args:
            @string: The string to generate an ID from.
        
        Returns:
            (str): The generated ID.
        """
        # Hash the input string using SHA-1
        hash_object = hashlib.sha1(string.encode())
        
        # Take the first 12 bytes of the hash
        objectid_hex = hash_object.hexdigest()[:24]
        
        # Create an ObjectId from the hex string
        object_id = ObjectId(objectid_hex)
        
        return object_id
    
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
            """
            Maps the attributes of a post to the post dictionary.
            
            Args:
                @post: The post dictionary.
                @attributes: The attributes of the post element.
            
            Returns:
                A dictionary containing the mapped post data.
            """
            """
            Maps the attributes of a post to the post dictionary.
            
            Args:
                @post: The post dictionary.
                @attributes: The attributes of the post element.
            
            Returns:
                A dictionary containing the mapped post data.
            """
            mapping = {
                'data-fullname': '_id',
                'data-timestamp': 'time',
                'data-permalink': 'url',
                'data-score': 'upvotes'
                'data-fullname': '_id',
                'data-timestamp': 'time',
                'data-permalink': 'url',
                'data-score': 'upvotes'
            }
            
            ## check if ad and skips if true
            ## attribute contains this field (data-promoted) so we can check if it's an ad -> doesn't work.. ?
            ## ads usually start with u/ instead of r/
            ## attribute contains this field (data-promoted) so we can check if it's an ad -> doesn't work.. ?
            ## ads usually start with u/ instead of r/
            ## attributes also contain data-nsfw for nsfw posts
            for attr in attributes:
                if attr['name'] == 'data-promoted' and attr['value'] == 'true':
                    return None
                    return None
                if attr['name'] in mapping:
                    post[mapping[attr['name']]] = attr['value']
            
            if post['timestamp']:
                timestamp_seconds = int(post['timestamp']) / 1000
                dt = datetime.datetime.fromtimestamp(timestamp_seconds)
                post['timestamp'] = dt
                
            if post['_id']:
                post['_id'] = await self.generate_id(post['_id'])
                
            if post['_id']:
                post['_id'] = await self.generate_id(post['_id'])
            
            return post
        
        #Helper Function
        async def process_element(page, element):
            """
            Processes a post element and extracts its data.
           
            Args:
                @page: The Playwright page object.
                @element: The post element.
            
            Returns:
                A dictionary containing the post data. 
            """
            """
            Processes a post element and extracts its data.
           
            Args:
                @page: The Playwright page object.
                @element: The post element.
            
            Returns:
                A dictionary containing the post data. 
            """
            post = {
                '_id':None,
                'url': None,
                '_id':None,
                'url': None,
                'title': '',
                'description': '',
                'time': None,
                'upvotes': None,
                'views': None,
                'reposts': None,
                'time': None,
                'upvotes': None,
                'views': None,
                'reposts': None,
            }
            attributes = await element.evaluate('el => { return Array.from(el.attributes).map(attr => ({name: attr.name, value: attr.value})); }')
            mapped_post = await map_post(post, attributes)
            if mapped_post is not None:
                post.update(mapped_post)
                data_fullname = next(attr['value'] for attr in attributes if attr['name'] == 'data-fullname')
                post['title'] = await (await page.query_selector(f"div[data-fullname='{data_fullname}'] > div.entry.unvoted > div.top-matter > p.title > a" )).inner_text()
                post['description'] = await (await page.query_selector(f"#form-{data_fullname} > div.usertext-body")).inner_text()
                post['description'] = await (await page.query_selector(f"#form-{data_fullname} > div.usertext-body")).inner_text()
                return post
            else:
                return None
            else:
                return None
        
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
                    'commentID': comment['id'],
                    'postID': post_id,
                    'parentId': comment['parentId'],
                    'comment': comment['comment'],
                    'score':  int(comment['score'].split()[0]) if comment['score'] else 0, # the score we get is a string with the score and the word 'points'
                    'level' : level,
                    'childrenIDs':comment['childrenIds']
                }
                if 'children' in comment and comment['children']:
                    processed_comment['children'] = await process_comments(comment['children'], post_id, level + 1)
                processed_comments.append(processed_comment)
            return processed_comments
        
        async def load_pages(page, post):
            await page.goto(f"https://old.reddit.com/{post['perma_link']}", wait_until='domcontentloaded')
            #get description
            #get description
            await page.wait_for_load_state('load')
            comment_data = await page.evaluate("""
<<<<<<< Updated upstream
                        (
                            function fetchComments() {
                            const allComments = [];

                            function getCommentData(commentElement, parentId = null) {
                                const data = {
                                    comment: commentElement.querySelector(".usertext")?.innerText,
                                    score: commentElement.querySelector(".score")?.innerText,
                                    fullname: commentElement.getAttribute("data-fullname"),
                                    id: commentElement.getAttribute("id"),
                                    parentId: parentId,
                                    childrenIds: Array.from(commentElement.querySelectorAll(":scope > .child > .listing > .comment"))
                                        .map(child => child.getAttribute("data-fullname"))
                                };

                                // extract all other attributes
                                Array.from(commentElement.attributes).forEach(attr => {
                                    data[attr.name] = attr.value;
                                });

                                // store the comment data in the allComments array
                                allComments.push(data);

                                // recursively process children comments
                                const childComments = commentElement.querySelectorAll(":scope > .child > .listing > .comment");
                                childComments.forEach(child => getCommentData(child, data.fullname));
                            }

                            const rootComments = document.querySelectorAll("div.commentarea > .sitetable > .comment");
                            rootComments.forEach(comment => getCommentData(comment));

                            return allComments;
                        })();
=======
                        (function fetchComments() {
                            function getCommentData(commentElement, parent_id =git  null) {
                                var id = commentElement.getAttribute("data-fullname");
                            function getCommentData(commentElement, parent_id =git  null) {
                                var id = commentElement.getAttribute("data-fullname");
                                var comment = commentElement.querySelector(".usertext")?.innerText;
                                var score = commentElement.querySelector(".score")?.innerText;
                                var childrenElements = Array.from(commentElement.querySelectorAll(":scope > .child > .listing > .comment"));
                                var children_ids = childrenElements.map(child => child.querySelector(".fullname")?.innerText);
                                var children = childrenElements.map(child => getCommentData(child, id));
                                return {id, comment, score, fullname, parent_id, children_ids, children};
                        }
                                var childrenElements = Array.from(commentElement.querySelectorAll(":scope > .child > .listing > .comment"));
                                var children_ids = childrenElements.map(child => child.querySelector(".fullname")?.innerText);
                                var children = childrenElements.map(child => getCommentData(child, id));
                                return {id, comment, score, fullname, parent_id, children_ids, children};
                        }

                    var rootComments = document.querySelectorAll("div.commentarea > .sitetable > .comment");
                    return Array.from(rootComments).map(comment => getCommentData(comment));
                    })()
>>>>>>> Stashed changes
                    """)

            comments_data = await process_comments(comment_data, post['_id'])
            comments_data = await process_comments(comment_data, post['_id'])
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
