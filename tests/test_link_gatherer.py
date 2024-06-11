import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, patch, call

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Scrapers.Twitter.TwitterScraperClass import TwitterScraper

def side_effect_values(values, default):
    iter_values = iter(values)
    def _side_effect(*args, **kwargs):
        try:
            return next(iter_values)
        except StopIteration:
            return default
    return _side_effect

@pytest_asyncio.fixture
async def scraper():
    return TwitterScraper(link_gather_account_username="DemoSprint4", link_gather_account_password="TestingTest", keyword="TestKeyword")

@pytest.mark.asyncio
async def test_link_gatherer_typing_and_search(scraper):
    mock_page = AsyncMock()

    # Mock the page's methods to return Futures that can be awaited
    mock_page.type.return_value = asyncio.Future()
    mock_page.type.return_value.set_result(None)
    mock_page.keyboard.press.return_value = asyncio.Future()
    mock_page.keyboard.press.return_value.set_result(None)

    await scraper.link_gatherer(mock_page)

    mock_page.type.assert_any_call('[data-testid="SearchBox_Search_Input"]', "TestKeyword min_faves:500 since:2024-01-01", delay=150)
    mock_page.keyboard.press.assert_any_call('Enter')

# @pytest.mark.asyncio
# async def test_link_gatherer_handle_cookies(scraper):
#     mock_page = AsyncMock()

#     # Create a mock element that has a click method
#     mock_cookies_button = AsyncMock()
#     mock_cookies_button.click.return_value = asyncio.Future()
#     mock_cookies_button.click.return_value.set_result(None)
    
#     # Simulate get_by_text returning the mock element directly
#     mock_page.get_by_text.return_value = mock_cookies_button

#     await scraper.link_gatherer(mock_page)

#     mock_page.get_by_text.assert_called_once_with("Refuse non-essential cookies")
#     mock_cookies_button.click.assert_called_once()

@pytest.mark.asyncio
async def test_link_gatherer_collecting_links(scraper):
    mock_page = AsyncMock()
    
    # Ensure get_by_text returns None (no cookies button)
    mock_page.get_by_text.return_value = None
    
    # Mock scrolling behavior
    mock_page.evaluate.side_effect = side_effect_values([1000, 2000, 3000, 4000], 4000)  # Simulating the page scroll height
    
    # Mock the query_selector_all to return a list of mocked elements
    mock_elements = [AsyncMock() for _ in range(3)]
    for i, elem in enumerate(mock_elements):
        elem.get_attribute.return_value = (f'/user/status/{i}')
    mock_page.query_selector_all.return_value = mock_elements

    links = await scraper.link_gatherer(mock_page)

    # Ensure the return is a list and not None
    assert links is not None
    assert isinstance(links, list)
    assert len(links) == 3
    assert "https://twitter.com/user/status/0" in links
    assert "https://twitter.com/user/status/1" in links
    assert "https://twitter.com/user/status/2" in links

    expected_scroll_calls = [call("window.scrollTo(0, document.body.scrollHeight)") for _ in range(2)]
    expected_height_calls = [call("document.body.scrollHeight") for _ in range(2)]
    mock_page.evaluate.assert_has_calls(expected_scroll_calls + expected_height_calls, any_order=True)
    mock_page.query_selector_all.call_count == 2

@pytest.mark.asyncio
async def test_link_gatherer_exit(scraper):
    mock_page = AsyncMock()
    
    # Ensure get_by_text returns None (no cookies button)
    mock_page.get_by_text.return_value = None
    
    # Mock scrolling behavior
    mock_page.evaluate.side_effect = side_effect_values([1000, 2000, 3000, 4000], 4000)  # Simulating the page scroll height
    
    # Mock the query_selector_all to return a list of mocked elements
    mock_elements = [AsyncMock() for _ in range(3)]
    for i, elem in enumerate(mock_elements):
        elem.get_attribute.return_value = (f'/user/status/{i}')
    mock_page.query_selector_all.return_value = mock_elements

    await scraper.link_gatherer(mock_page)

    # Ensure the logout navigation is called
    mock_page.goto.assert_called_once_with('https://twitter.com/logout')
    mock_page.close.assert_called_once()
