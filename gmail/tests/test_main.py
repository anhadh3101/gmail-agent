import pytest
from unittest.mock import Mock
from app.main import fetch_recent_emails
from app.model import EmailPreview, FetchRecentEmailsRequest, FetchRecentEmailsResponse

def test_fetch_recent_emails_success(mocker):
    """
    Test successful email retrieval with valid access token.
    """
    # Arrange
    access_token = "test_access_token_12345"
    
    # Mock email data
    mock_emails = [
        EmailPreview(
            id="email_1",
            thread_id="thread_1",
            snippet="Test email 1",
            from_="test1@example.com",
            subject="Subject 1"
        ),
        EmailPreview(
            id="email_2",
            thread_id="thread_2",
            snippet="Test email 2",
            from_="test2@example.com",
            subject="Subject 2"
        ),
    ]
    
    mock_get = mocker.patch("app.main.get_all_threads")
    mock_get.return_value = mock_emails
    
    # Act
    result = fetch_recent_emails(access_token)
    
    # Assert    
    # Assert: Verify return type
    assert isinstance(result, FetchRecentEmailsResponse)
    
    assert len(result.emails) == 2
    assert result.emails[0].id == "email_1"
    assert result.emails[0].thread_id == "thread_1"
    assert result.emails[0].from_ == "test1@example.com"
    assert result.emails[0].subject == "Subject 1"
    assert result.emails[1].id == "email_2"
    assert result.emails[1].thread_id == "thread_2"
    assert result.emails[1].from_ == "test2@example.com"
    assert result.emails[1].subject == "Subject 2"
    
    # Verify get_all_threads was called with correct parameters
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    # access_token is passed as positional argument (first arg)
    assert call_args.args[0] == access_token
    # max_threads is passed as keyword argument
    assert call_args.kwargs["max_threads"] == 20