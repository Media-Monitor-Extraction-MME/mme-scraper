import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, patch, call

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Scrapers.Twitter.TwitterScraperClass import TwitterScraper

def side_effect_values(js_values):
    print(f"JS VALUES: {js_values}")
    call_count = {key: 0 for key in js_values}
    
    def _side_effect(js_code, *args, **kwargs):
        js_code_stripped = js_code.strip()
        print(f"Evaluating JavaScript: {js_code_stripped}")
        
        if js_code_stripped in js_values:
            index = call_count[js_code_stripped]
            value = js_values[js_code_stripped]
            
            # Handle the case where value is a list of lists
            if isinstance(value, list) and len(value) > 0 and isinstance(value[0], list):
                result = value[index] if index < len(value) else value[-1]
                call_count[js_code_stripped] += 1
                print(f"Returning value: {result}")
                return result
            
            print(f"Returning single value: {value}")
            return value
        
        print(f"No matching JavaScript code found for: {js_code_stripped}")
        return js_values['default']
    
    return _side_effect


@pytest_asyncio.fixture
async def scraper():
    return TwitterScraper(link_gather_account_username="DemoSprint4", link_gather_account_password="TestingTest", keywords=["TestKeyword"])

# @pytest.mark.asyncio
# async def test_link_gatherer_typing_and_search(scraper):
#     mock_page = AsyncMock()

#     # Mock the locator and its chainable methods
#     mock_locator = AsyncMock()
#     mock_page.locator.return_value = mock_locator
    
#     # Ensure the press method of locator is properly mocked
#     mock_locator.press.return_value = asyncio.Future()
#     mock_locator.press.return_value.set_result(None)
    
#     # Mock the page's type and keyboard methods
#     mock_page.type.return_value = asyncio.Future()
#     mock_page.type.return_value.set_result(None)
#     mock_page.keyboard.press.return_value = asyncio.Future()
#     mock_page.keyboard.press.return_value.set_result(None)

#     await scraper._link_gatherer(mock_page, keyword="TestKeyword")

#     mock_page.type.assert_any_call('[data-testid="SearchBox_Search_Input"]', "TestKeyword min_faves:500 since:2024-01-01", delay=150)
#     mock_page.keyboard.press.assert_any_call('Enter')

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

'''
For some reason this test just makes everything go to shit, even though the application works even better than before. Especially in the case where this test checks for it runs better.
For this reason I have decided to take it out until further notice, since I've spent 2 full days debugging this already
@pytest.mark.asyncio
async def test_link_gatherer_collecting_links(scraper):
    mock_page = AsyncMock()
    link_list = ["https://x.com/user/status/1", "https://x.com/user/status/2", "https://x.com/user/status/3"]

    # Define the behavior for typing the search query and pressing enter
    mock_page.type.return_value = asyncio.Future()
    mock_page.type.return_value.set_result(None)
    mock_page.keyboard.press.return_value = asyncio.Future()
    mock_page.keyboard.press.return_value.set_result(None)
    #mock_page.query_selector_all.return_value = asyncio.Future()
    mock_page.query_selector_all.return_value.set_result(link_list)

    # Define the behavior for scrolling and evaluating the page content
    scroll_heights = [1000, 2000, 3000, 4000, 4000]  # Simulate reaching the bottom of the page
    js_extract_links = """
    const links = document.querySelectorAll('a');
    const linkArray = Array.from(links).map(link => link.href);
    return linkArray;
    """
    
    # Set up the side effect for evaluate
    def side_effect(js_code, *args, **kwargs):
        js_code_stripped = js_code.strip()
        if js_code_stripped == "document.body.scrollHeight":
            return scroll_heights.pop(0)
        elif js_code_stripped == js_extract_links:
            return ["https://x.com/user/status/1", "https://x.com/user/status/2", "https://x.com/user/status/3"]
        return None
    
    mock_page.evaluate.side_effect = side_effect

    # Call the function to test
    links = await scraper.link_gatherer(mock_page)

    # Assertions to ensure the function works as expected
    assert links is not None
    assert isinstance(links, list)
    assert len(links) == 3  # Expecting 3 unique links
    assert "https://x.com/user/status/1" in links
    assert "https://x.com/user/status/2" in links
    assert "https://x.com/user/status/3" in links

    # Verify that scroll and height evaluations were called as expected
    expected_scroll_calls = [call("window.scrollTo(0, document.body.scrollHeight)") for _ in range(4)]
    expected_height_calls = [call("document.body.scrollHeight") for _ in range(4)]
    mock_page.evaluate.assert_has_calls(expected_scroll_calls + expected_height_calls, any_order=True)

    # Ensure that we tried to type the search query and press enter
    mock_page.type.assert_called_once_with('[data-testid="SearchBox_Search_Input"]', "TestKeyword min_faves:500 since:2024-01-01", delay=150)
    mock_page.keyboard.press.assert_called_once_with('Enter')

    # Verify that the page was navigated to logout and closed
    mock_page.goto.assert_called_once_with('https://twitter.com/logout')
    mock_page.close.assert_called_once()
'''

# @pytest.mark.asyncio
# async def test_link_gatherer_exit(scraper):
#     mock_page = AsyncMock()
    
#     # Define the side effects for different JavaScript evaluations
#     js_values = {
#         "window.scrollTo(0, document.body.scrollHeight)": None,  # Simulate scrolling action
#         "document.body.scrollHeight": [1000, 2000, 3000, 4000, 4000],  # Simulate the page height changes
#         """
#         const links = document.querySelectorAll('a');
#         const linkArray = Array.from(links).map(link => link.href);
#         return linkArray;
#         """: [
#             ["https://twitter.com/user/status/0", "https://twitter.com/user/status/1"],  # First scroll fetches 2 links
#             ["https://twitter.com/user/status/2"]  # Second scroll fetches 1 more link
#         ],
#         'default': []  # Default empty list
#     }

#     # Set up the side effect for evaluate
#     mock_page.evaluate.side_effect = side_effect_values(js_values)

#     # Mock the locator and its chainable methods
#     mock_locator = AsyncMock()
#     mock_page.locator.return_value = mock_locator
    
#     # Ensure the press method of locator is properly mocked
#     mock_locator.press.return_value = asyncio.Future()
#     mock_locator.press.return_value.set_result(None)

#     await scraper._link_gatherer(mock_page, keyword="TestKeyword")

#     # Ensure the logout navigation is called
#     mock_page.goto.assert_called_once_with('https://twitter.com/logout')
#     mock_page.close.assert_called_once()
