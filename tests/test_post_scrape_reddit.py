import pytest
import os, sys
from unittest.mock import AsyncMock
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Scrapers.Reddit.RedditScraperClass import RedditScraper

@pytest.mark.asyncio
async def test_post_scrape():
    mock_subreddit = "r/test"
    mock_post_results = [{'_id': 1,
                          'url': "https://old.reddit.com/r/test/comments/1",
                          'title': "Test Post 1",
                          'description': "This is a test post",
                          'time': "1 hour ago",
                          'upvotes': 100},
                         {'_id': 2,
                          'url': "https://old.reddit.com/r/test/comments/2",
                          'title': "Test Post 2",
                          'description': "This is another test post",
                          'time': "2 hours ago",
                          'upvotes': 200}]
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page