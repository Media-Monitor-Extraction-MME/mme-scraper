
import pytest
import pytest_asyncio
import os, sys
from unittest.mock import AsyncMock, MagicMock, patch
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Scrapers.Reddit.RedditScraperClass import RedditScraper

@pytest.fixture
def mock_nodelist():
    pass

@pytest.mark.asyncio
async def test_content_scrape():
    mock_posts = [
    {
        'postID': 1,
        'url': 'r/test/comments/1',
        'title': 'First Post Title',
        'description': 'Description of the first post.',
        'time': '2023-04-01T12:00:00',
        'upvotes': 150
    },
    {
        'postID': 2,
        'url': 'r/test/comments/2',
        'title': 'Second Post Title',
        'description': 'Description of the second post, with more details.',
        'time': '2023-04-02T15:30:00',
        'upvotes': 250
    },
    {
        'postID': 3,
        'url': 'r/test/comments/3',
        'title': 'Third Post Title',
        'description': 'This is a short description of the third post.',
        'time': '2023-04-03T18:45:00',
        'upvotes': 75
    }
    ]
    
    
    mock_comment_data = [
        {
            'comment': "Test Comment 1",
            'score': "10 points",
            'fullname': "t1_1",
            'id': "c1",
            'parentId': None,
            'childrenIds': ["t1_2"]
        },
        {
            'comment': "Test Comment 2",
            'score': "5 points",
            'fullname': "t1_2",
            'id': "c2",
            'parentId': "t1_1",
            'childrenIds': []
        }
    ]
    
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()

    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page

    mock_page.goto.return_value = None
    mock_page.wait_for_load_state.return_value = None
    
    mock_page.evaluate.return_value = mock_comment_data
    
    mock_page.query_selector.return_value = AsyncMock(inner_text=AsyncMock(return_value="Test Description"))
    
    scraper = RedditScraper(query="test")

    result = await scraper._content_scrape(posts=mock_posts, browser=mock_browser)
        
    mock_page.goto.assert_any_call("https://old.reddit.com/r/test/comments/1", wait_until='domcontentloaded')
    mock_page.goto.assert_any_call("https://old.reddit.com/r/test/comments/2", wait_until='domcontentloaded')
    mock_page.wait_for_load_state.assert_called_with("load")
    mock_page.evaluate.assert_called()
    
    assert result is not None, "Result should not be None"
    assert isinstance(result, list), "Result should be a list of comments"
    assert len(result) == 6, "Result should contain 2x3 comments, 2 comments per post"
    assert result[0]['comment'] == "Test Comment 1"
    assert result[1]['comment'] == "Test Comment 2"