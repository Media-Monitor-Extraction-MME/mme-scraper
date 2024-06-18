import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, patch
# import aiohttp
from bson import ObjectId

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Scrapers.Twitter.TwitterScraperClass import TwitterScraper

@pytest_asyncio.fixture
async def scraper():
    return TwitterScraper(link_gather_account_username="DemoSprint4", link_gather_account_password="TestingTest", keyword="TestKeyword")

# Example response to mock the API call
example_response = {
    'text': 'Sample tweet content with emoji 😊',
    'created_at': '2024-06-10T12:34:56Z',
    'favorite_count': 123
}

@pytest.mark.asyncio
async def test_fetch_single_tweet(scraper):
    #Mocking aiohttp.ClientSession.get
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=example_response)
        mock_get.return_value.__aenter__.return_value = mock_response


        #Just a test link below
        link = "https://x.com/JamesLucasIT/status/1799856071609049548"

        #Make function call
        tweets = await scraper._api_implementation([link])

        #Validate
        assert len(tweets) == 1
        tweet = tweets[0]
        assert tweet['_id'] == ObjectId("000001799856071609049548")
        assert tweet['url'] == '/JamesLucasIT/status/1799856071609049548'
        assert tweet['description'] == 'Sample tweet content with emoji 😊'
        assert tweet['time'] == '2024-06-10T12:34:56Z'
        assert tweet['upvotes'] == 123

@pytest.mark.asyncio
async def test_api_implementation_multiple_links(scraper):
    #Mocking aiohttp.ClientSession.get
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=example_response)
        mock_get.return_value.__aenter__.return_value = mock_response
        
        links = [
            "https://x.com/i/status/1225070587397246976",
            "https://x.com/JamesLucasIT/status/1799856071609049548"
        ]

        #Make function call
        tweets = await scraper._api_implementation(links)

        #Validate
        assert len(tweets) == 2
        for tweet in tweets:
            assert tweet['description'] == 'Sample tweet content with emoji 😊'
            assert tweet['time'] == '2024-06-10T12:34:56Z'
            assert tweet['upvotes'] == 123



