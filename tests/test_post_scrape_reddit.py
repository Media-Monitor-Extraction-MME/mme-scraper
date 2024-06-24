import pytest
import pytest_asyncio
import os,sys
from unittest.mock import AsyncMock, MagicMock
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Scrapers.Reddit.RedditScraperClass import RedditScraper

@pytest.fixture
def mock_nodelist():
    # Create mock elements
    mock_element1 = MagicMock()
    mock_element2 = MagicMock()

    # Mock the evaluate method for each element
    mock_element1.evaluate = AsyncMock(return_value=[
        {'name': 'data-fullname', 'value': 't3_1'},
        {'name': 'data-timestamp', 'value': '1609459200000'},  # January 1, 2021
        {'name': 'data-permalink', 'value': '/r/test/comments/1'},
        {'name': 'data-score', 'value': '100'}
    ])
    mock_element2.evaluate = AsyncMock(return_value=[
        {'name': 'data-fullname', 'value': 't3_2'},
        {'name': 'data-timestamp', 'value': '1609459200000'},  # January 1, 2021
        {'name': 'data-permalink', 'value': '/r/test/comments/2'},
        {'name': 'data-score', 'value': '200'}
    ])

    # Mock the inner_text method for title and description
    mock_element1.query_selector = AsyncMock(return_value=AsyncMock(inner_text=AsyncMock(return_value="Mock Title 1")))
    mock_element2.query_selector = AsyncMock(return_value=AsyncMock(inner_text=AsyncMock(return_value="Mock Title 2")))
    
    mock_element1.query_selector.side_effect = lambda selector: AsyncMock(inner_text=AsyncMock(return_value="Mock Description 1")) if "usertext-body" in selector else AsyncMock(inner_text=AsyncMock(return_value="Mock Title 1"))
    mock_element2.query_selector.side_effect = lambda selector: AsyncMock(inner_text=AsyncMock(return_value="Mock Description 2")) if "usertext-body" in selector else AsyncMock(inner_text=AsyncMock(return_value="Mock Title 2"))

    # Create the mock NodeList
    mock_nodelist = [mock_element1, mock_element2]

    return mock_nodelist

@pytest.mark.asyncio
async def test_post_scrape(mock_nodelist):
    mock_forums = ["r/test", "r/test2", "r/test3"]
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()

    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page

    mock_page.goto.return_value = None
    mock_page.wait_for_load_state.return_value = None
    mock_page.query_selector_all.return_value = mock_nodelist

    scraper = RedditScraper(query="test")

    result = await scraper._post_scrape(forums=mock_forums, browser=mock_browser)
    
    # Assert that the expected methods were called on the mock objects
    mock_page.goto.assert_any_call("https://old.reddit.com/r/test", wait_until='domcontentloaded')
    mock_page.goto.assert_any_call("https://old.reddit.com/r/test2", wait_until='domcontentloaded')
    mock_page.goto.assert_any_call("https://old.reddit.com/r/test3", wait_until='domcontentloaded')
    mock_page.wait_for_load_state.assert_called_with("load")
    mock_page.query_selector_all.assert_called_with('div[data-fullname]')

    assert result is not None, "Result should not be None"
    assert isinstance(result, list), "Result should be a list of posts"
    assert len(result) == 2, "Result should contain 2 posts"
    assert result[0]['postID'] == 't3_1'
    assert result[1]['postID'] == 't3_2'