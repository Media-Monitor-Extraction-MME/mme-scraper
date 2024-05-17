'''
Reddit scraper implementation
'''

#Imports

class RedditScraper:
    
    #Fields
    query = str
    selector = str
    keywords = [str]

    def __init__(self, query, selector):
        self.query = query
        self.selector = selector
        pass

    #Methods
    async def subreddit_scrape(self, frequency, keywords) -> list:
        ...

    async def post_scrape(self, forums) -> dict:
        ...

    async def content_scrape(self, posts) -> dict:
        ...