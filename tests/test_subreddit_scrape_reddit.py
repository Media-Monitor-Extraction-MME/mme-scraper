import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock
from Scrapers.Reddit.RedditScraperClass import RedditScraper


@pytest.mark.asyncio
async def test_subreddit_scrape():
    query = "test"
    mock_search_results = ['r/subreddit1', 'r/subreddit2']
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    
    mock_search_results = [AsyncMock(), AsyncMock()]
    mock_page.query_seletor_all.return_value = mock_search_results
    
    for result in mock_search_results:
        result.query_selector.side_effeft = [AsyncMock(), AsyncMock()]
        
    def query_selector_side_effect(selector):
        if selector == 'a.search-title':
            return AsyncMock(inner_text="subreddit1")
        elif selector == 'span.search-subscribers':
            return AsyncMock(inner_text="3,000")
        else:
            return None

    for result in mock_search_results:
        result.query_selector.side_effect = query_selector_side_effect
        scraper = RedditScraper(query=query)
    
    result = await scraper._subreddit_scrape(mock_browser)
    
    mock_browser.new_context.assert_called_once()
    mock_context.new_page.assert_called_once()
    mock_page.goto.assert_called_once_with(f"https://old.reddit.com/search/?q={query}&type=sr")
    mock_page.wait_for_load_state.assert_called_once_with("load")
    mock_page.query_selector_all.assert_called_once_with("div[data-fullname]")
    
    assert isinstance(result, list), "Result should be a list of subreddits"