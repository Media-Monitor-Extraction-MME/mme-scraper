import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock
from Scrapers.Reddit.RedditScraperClass import RedditScraper


@pytest.mark.asyncio
async def test_subreddit_scrape():
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    
    mock_search_results = [AsyncMock(), AsyncMock()]
    mock_page.query_seletor_all.return_value = mock_search_results
    
    for result in mock_search_results:
        result.query_selector.side_effeft = [AsyncMock(), AsyncMock()]
        
    for result in mock_search_results:
        for element in result.query_selector.side_effect:
            element.inner_text.side_effect = ["subreddit1", "3,000"]
            
    scraper = RedditScraper(query="test")
    
    result = await scraper._subreddit_scrape(mock_browser)
    assert result == ["subreddit1"]
    
    mock_browser.new_context.assert_called_once()
    mock_context.new_page.assert_called_once()
    mock_page.goto.assert_called_once_with("https://www.reddit.com/subreddits/search?q=test")
    mock_page.wait_for_load_state.assert_called_once_with("load")
    mock_page.query_selector_all.assert_called_once_with("div[date-fullname]")
    
    