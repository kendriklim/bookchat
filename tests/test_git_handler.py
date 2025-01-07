#!/usr/bin/env python3

import pytest
import os
from datetime import datetime, timezone
import uuid
from unittest.mock import Mock, patch
from src.git_handler import GitHandler
from github import GithubException, Auth

# Test fixtures
@pytest.fixture
def mock_github():
    """Create a mock GitHub API"""
    with patch('github.Github') as mock:
        # Mock the auth
        mock_auth = Mock()
        mock.Auth = Mock()
        mock.Auth.Token = Mock(return_value=mock_auth)
        
        # Mock the user
        mock_user = Mock()
        mock.return_value.get_user.return_value = mock_user
        
        # Mock the repository
        mock_repo = Mock()
        mock_user.get_repo.return_value = mock_repo
        mock_user.create_repo.return_value = mock_repo
        
        # Mock the contents
        mock_content = Mock()
        mock_content.path = "messages/test.json"
        mock_content.decoded_content = b'{"id": "test", "content": "test", "timestamp": "2025-01-07T20:00:00+00:00"}'
        mock_content.sha = "test_sha"
        mock_repo.get_contents.return_value = [mock_content]
        
        # Mock file operations
        mock_repo.create_file.return_value = {"content": mock_content}
        mock_repo.update_file.return_value = {"content": mock_content}
        
        yield mock

@pytest.fixture
def git_handler(mock_github):
    """Create a GitHandler instance for testing"""
    with patch.dict(os.environ, {
        'GITHUB_TOKEN': 'test_token',
        'GITHUB_REPO': 'test_repo',
        'GITHUB_USERNAME': 'test_user'
    }):
        return GitHandler()

@pytest.fixture
def test_message():
    """Create a test message"""
    return {
        'id': str(uuid.uuid4()),
        'content': 'Test message content',
        'author': 'test_user',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }

# Test cases
def test_git_handler_initialization():
    """Test GitHandler initialization with environment variables"""
    with patch.dict(os.environ, {
        'GITHUB_TOKEN': 'test_token',
        'GITHUB_REPO': 'test_repo',
        'GITHUB_USERNAME': 'test_user'
    }):
        handler = GitHandler()
        assert handler.token is not None
        assert handler.repo_name is not None
        assert handler.username is not None

def test_get_or_create_repo(git_handler, mock_github):
    """Test repository retrieval or creation"""
    repo = git_handler.get_or_create_repo()
    assert repo is not None

def test_save_message(git_handler, test_message, mock_github):
    """Test saving a message to GitHub"""
    success, result = git_handler.save_message(test_message)
    assert success is True
    assert isinstance(result, str)
    assert test_message['id'] in result

def test_get_messages(git_handler, mock_github):
    """Test retrieving messages from GitHub"""
    success, messages = git_handler.get_messages(limit=5)
    assert success is True
    assert isinstance(messages, list)
    if messages:
        assert all(isinstance(m, dict) for m in messages)
        assert all('content' in m for m in messages)
        assert all('timestamp' in m for m in messages)

def test_update_message(git_handler, test_message, mock_github):
    """Test updating an existing message"""
    # First, save a message
    success, filename = git_handler.save_message(test_message)
    assert success is True

    # Then update it
    new_content = "Updated test message content"
    success, updated_message = git_handler.update_message(test_message['id'], new_content)
    assert success is True
    assert updated_message['content'] == new_content
    assert 'updated_at' in updated_message

def test_message_ordering(git_handler, mock_github):
    """Test that messages are returned in correct order"""
    success, messages = git_handler.get_messages()
    assert success is True
    if len(messages) >= 2:
        # Check that messages are ordered by timestamp (newest first)
        timestamps = [m['timestamp'] for m in messages]
        assert timestamps == sorted(timestamps, reverse=True)

def test_invalid_message_update(git_handler, mock_github):
    """Test updating a non-existent message"""
    success, error = git_handler.update_message(
        str(uuid.uuid4()),  # Random non-existent ID
        "This update should fail"
    )
    assert success is False
    assert isinstance(error, str)

def test_message_limit(git_handler, mock_github):
    """Test the message limit parameter"""
    limit = 3
    success, messages = git_handler.get_messages(limit=limit)
    assert success is True
    assert len(messages) <= limit

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
