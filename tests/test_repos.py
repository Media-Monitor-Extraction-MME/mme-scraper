import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, patch

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from General.RepoStructure.Repos import CommentRepo, PostRepo

#Mock DB class
@pytest.fixture
def mock_db_manager():
    return AsyncMock()

#####################
#Test for CommentRepo
#####################
@pytest.mark.asyncio
async def test_add_post(mock_db_manager):
    comment_repo = CommentRepo(mock_db_manager, "comments")
    document = {"content": "This is a test comment"}
    await comment_repo.add_comment([document])
    mock_db_manager.insert_documents.assert_awaited_once_with("comments", document)

@pytest.mark.asyncio
async def test_remove_comment(mock_db_manager):
    comment_repo = CommentRepo(mock_db_manager, "comments")
    filter = {"id": "123"}
    await comment_repo.remove_comment(filter)
    mock_db_manager.delete_documents.assert_awaited_once_with("comments", filter)

@pytest.mark.asyncio
async def test_update_comment(mock_db_manager):
    comment_repo = CommentRepo(mock_db_manager, "comments")
    filter = {"id": "123"}
    document = {"content": "Updated comment."}
    await comment_repo.update_comment(filter, document)
    mock_db_manager.update_documents.assert_awaited_once_with("comments", filter, document)

@pytest.mark.asyncio
async def test_search_comment(mock_db_manager):
    comment_repo = CommentRepo(mock_db_manager, "comments")
    filter = {"id": "123"}
    await comment_repo.search_comment(filter)
    mock_db_manager.get_document.assert_awaited_once_with("comments", filter)


###################
#Tests for PostRepo
###################
@pytest.mark.asyncio
async def test_add_post(mock_db_manager):
    post_repo = PostRepo(mock_db_manager, "posts")
    document = {"content": "This is a test post"}
    await post_repo.add_post([document])
    mock_db_manager.insert_documents.assert_awaited_once_with("posts", document)

@pytest.mark.asyncio
async def test_remove_post(mock_db_manager):
    post_repo = PostRepo(mock_db_manager, "posts")
    filter = {"id": "123"}
    await post_repo.remove_post(filter)
    mock_db_manager.delete_documents.assert_awaited_once_with("posts", filter)

@pytest.mark.asyncio
async def test_update_post(mock_db_manager):
    post_repo = PostRepo(mock_db_manager, "posts")
    filter = {"id": "123"}
    document = {"content": "Updated post."}
    await post_repo.update_post(filter, document)
    mock_db_manager.update_documents.assert_awaited_once_with("posts", filter, document)

@pytest.mark.asyncio
async def test_search_post(mock_db_manager):
    post_repo = PostRepo(mock_db_manager, "posts")
    filter = {"id": "123"}
    await post_repo.search_post(filter)
    mock_db_manager.get_document.assert_awaited_once_with("posts", filter)
