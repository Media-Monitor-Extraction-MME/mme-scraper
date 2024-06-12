import pytest
import pytest_asyncio
import pytest_playwright
import asyncio
from unittest.mock import AsyncMock, patch
import logging

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Scrapers.Twitter.TwitterScraperClass import TwitterScraper

@pytest_asyncio.fixture
async def scraper():
    return TwitterScraper(link_gather_account_username="DemoSprint4", link_gather_account_password="TestingTest", keyword="TestKeyword")

@pytest.mark.asyncio
async def test_login_browser_success(scraper):
    #Mock browser and page
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()

    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page

    #Mock behaviour of page methods
    mock_page.goto.return_value = asyncio.Future()
    mock_page.goto.return_value.set_result(None)
    mock_page.type.return_value = asyncio.Future()
    mock_page.type.return_value.set_result(None)
    mock_page.click.return_value = asyncio.Future()
    mock_page.click.return_value.set_result(None)
    mock_page.wait_for_load_state.return_value = asyncio.Future()
    mock_page.wait_for_load_state.return_value.set_result(None)

    result = await scraper.login_account(mock_browser)

    assert result == mock_page
    mock_browser.new_context.assert_called_once_with(no_viewport=True)
    mock_context.new_page.assert_called_once()
    mock_page.goto.assert_called_once_with("https://twitter.com/i/flow/login")
    mock_page.type.assert_any_call('input[type="text"][name="text"]', "DemoSprint4", delay=150)
    mock_page.type.assert_any_call('input[name="password"]', "TestingTest", delay=150)
    mock_page.click.assert_any_call("text='Next'")
    mock_page.click.assert_any_call('[data-testid="LoginForm_Login_Button"]')
    mock_page.wait_for_load_state.assert_called_once()

@pytest.mark.asyncio
async def test_login_account_failure(scraper):
    # Mocking browser and page
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()

    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page

    # Mocking an exception during the login process
    mock_page.goto.side_effect = Exception("Test error")

    result = await scraper.login_account(mock_browser)

    assert result is None
    mock_browser.new_context.assert_called_once_with(no_viewport=True)
    mock_context.new_page.assert_called_once()
    mock_page.goto.assert_called_once_with("https://twitter.com/i/flow/login")
    logging.error("An error occurred: Test error")
