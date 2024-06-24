import pytest
import pytest_asyncio
import os, sys
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Scrapers.Reddit.RedditScraperClass import RedditScraper

@pytest.fixture
def mock_launch_contexts():
    return AsyncMock()

@pytest.fixture
def mock_process_element():
    return AsyncMock()

@pytest.fixture
def mock_element():
    return MagicMock()

@pytest.fixture
def mock_forums():
    return ["r/test", "r/test2", "r/test3"]

@pytest.mark.asyncio
async def test_post_scrape(mock_process_element, mock_element, mock_forums):
    mock_posts = [
                {
                '_id': 1,
                'url': "https://old.reddit.com/r/test/comments/1",
                'title': "Test Post 1",
                'description': "This is a test post",
                'timestamp': datetime(2024, 1, 1),
                'upvotes': 100},
                {
                '_id': 2,
                'url': "https://old.reddit.com/r/test/comments/2",
                'title': "Test Post 2",
                'description': "This is another test post",
                'timestamp': datetime(2024, 1, 1),
                'upvotes': 200
            }
                ]
    
    def query_selector_side_effect(selector):
        if 'title' in selector:
            mock = AsyncMock()
            mock.inner_text = "Mock Title"
            return mock
        elif 'usertext-body' in selector:
            mock = AsyncMock()
            mock.inner_text = "Mock Description"
            return mock
        else:
            return None
            
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    mock_element = AsyncMock()
    mock_launch_contexts = AsyncMock()
    
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page

    mock_page.goto.return_value = None
    mock_page.wait_for_load_state.return_value = None
    mock_page.query_selector_all.return_value = [mock_element]
    mock_page.query_selector.side_effect = query_selector_side_effect
    mock_process_element.return_value = mock_posts
    mock_element.evaluate.return_value = AsyncMock()
    scraper = RedditScraper(query='test')
    with patch.object(scraper, '_post_scrape', new=mock_process_element):
        result =  await scraper._post_scrape(forums=mock_forums, browser=mock_browser)
    
    mock_launch_contexts.assert_called_once_with(forums=mock_forums,browser=mock_browser,return_value=mock_posts)
    
# Assert that the expected methods were called on the mock objects
    mock_process_element.assert_called_with(mock_page, mock_element)
    
    assert result is not None, "Result should not be None"
    assert isinstance(result, list), "Result should be a list of posts"
    assert result == mock_posts, "Result should be the same as the mock post"    
        
    
    