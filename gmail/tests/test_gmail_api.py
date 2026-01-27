import pytest
from unittest.mock import Mock, patch
import requests
from app.gmail_api import batch_get_threads, get_recent_thread_ids, get_all_threads


def test_get_recent_thread_ids_success(mocker):
    """
    Test successful thread ID retrieval with valid access token.
    """
    # Arrange
    access_token = "test_access_token_12345"
    max_results = 10
    
    # Mock response data
    mock_threads_data = {
        "threads": [
            {"id": "thread_1", "snippet": "Test email 1"},
            {"id": "thread_2", "snippet": "Test email 2"},
            {"id": "thread_3", "snippet": "Test email 3"},
        ]
    }
    # Create a mock response object
    mock_response = Mock()
    mock_response.json.return_value = mock_threads_data
    mock_response.raise_for_status = Mock()
    
    # Mock requests.get
    mock_get = mocker.patch("app.gmail_api.requests.get")
    mock_get.return_value = mock_response
    
    # Act
    result = get_recent_thread_ids(access_token, max_results)
    
    # Assert
    assert result == mock_threads_data["threads"]
    assert len(result) == 3
    assert result[0]["id"] == "thread_1"
    assert result[1]["id"] == "thread_2"
    assert result[2]["id"] == "thread_3"
    
    # Verify requests.get was called with correct parameters
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert call_args.kwargs["headers"]["Authorization"] == f"Bearer {access_token}"
    assert call_args.kwargs["params"]["q"] == "newer_than:1d"
    assert call_args.kwargs["params"]["maxResults"] == max_results
    
    # Verify raise_for_status was called
    mock_response.raise_for_status.assert_called_once()

def test_get_recent_thread_ids_invalid_token(mocker):
    """
    Test invalid token retrieval with invalid access token.
    """
    # Arrange
    access_token = "invalid_access_token_12345"
    max_results = 10
    
    # Create a mock response object that simulates 401 Unauthorized
    mock_response = Mock()
    mock_response.status_code = 401
    
    # Make raise_for_status raise an HTTPError
    http_error = requests.exceptions.HTTPError("401 Client Error: Unauthorized")
    mock_response.raise_for_status.side_effect = http_error
    
    # Mock requests.get
    mock_get = mocker.patch("app.gmail_api.requests.get")
    mock_get.return_value = mock_response
    
    # Act & Assert
    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        get_recent_thread_ids(access_token, max_results)
    
    # Verify the exception message
    assert "401" in str(exc_info.value) or "Unauthorized" in str(exc_info.value)
    
    # Verify requests.get was called with correct parameters
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert call_args.kwargs["headers"]["Authorization"] == f"Bearer {access_token}"
    assert call_args.kwargs["params"]["q"] == "newer_than:1d"
    assert call_args.kwargs["params"]["maxResults"] == max_results
    
    # Verify raise_for_status was called
    mock_response.raise_for_status.assert_called_once()

def test_get_recent_thread_ids_empty_response(mocker):
    """
    Test empty response retrieval with valid access token.
    """
    # Arrange
    access_token = "test_access_token_12345"
    max_results = 10
    
    # Create a mock response object that simulates an empty response
    mock_response = Mock()
    mock_response.json.return_value = {"threads": []}
    mock_response.raise_for_status = Mock()
    
    # Mock requests.get
    mock_get = mocker.patch("app.gmail_api.requests.get")
    mock_get.return_value = mock_response
    
    # Act
    result = get_recent_thread_ids(access_token, max_results)
    
    # Assert
    assert result == []
    assert len(result) == 0
    
    # Verify requests.get was called with correct parameters
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert call_args.kwargs["headers"]["Authorization"] == f"Bearer {access_token}"
    assert call_args.kwargs["params"]["q"] == "newer_than:1d"
    assert call_args.kwargs["params"]["maxResults"] == max_results
    
    # Verify raise_for_status was called
    mock_response.raise_for_status.assert_called_once()
    
def test_batch_get_threads_success(mocker):
    """
    Test successful batch thread retrieval with valid access token.
    """
    # Arrange
    access_token = "test_access_token_12345"
    boundary = "batch_0123455789"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": f"multipart/mixed; boundary={boundary}",
    }
    batch_body = (
        f"--{boundary}\n"
        "Content-Type: application/http\n"
        f"Content-ID: <request-1>\n\n"
        "GET /gmail/v1/users/me/threads/thread_1?format=full HTTP/1.1\n\n"
        f"--{boundary}--\n"
    )
    
    # Create a mock response object
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.headers = {"Content-Type": f"multipart/mixed; boundary={boundary}"}
    mock_response.text = "mock batch reponse"
    
    # Mock requests.post
    mock_post = mocker.patch("app.gmail_api.requests.post")
    mock_post.return_value = mock_response
    
    # Act
    result = batch_get_threads(access_token, headers, batch_body)
    
    # Assert
    assert result == mock_response
    
    # Verify requests.post was called with correct parameters
    mock_post.assert_called_once()
    
    call_args = mock_post.call_args
    assert call_args.kwargs["headers"] == headers
    assert call_args.kwargs["data"] == batch_body
    assert call_args.args[0] == "https://gmail.googleapis.com/batch/gmail/v1"
    
    mock_response.raise_for_status.assert_called_once()


def test_batch_get_threads_partial_failure(mocker):
    """
    Test batch request where some threads fail.
    The function should still return the response, but parse_gmail_batch_response
    will skip failed requests (non-200 responses).
    """
    # Arrange
    access_token = "test_access_token_12345"
    boundary = "batch_0123455789"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": f"multipart/mixed; boundary={boundary}",
    }
    batch_body = (
        f"--{boundary}\n"
        "Content-Type: application/http\n"
        "Content-ID: <request-1>\n\n"
        "GET /gmail/v1/users/me/threads/thread_1?format=full HTTP/1.1\n\n"
        f"--{boundary}\n"
        "Content-Type: application/http\n"
        "Content-ID: <request-2>\n\n"
        "GET /gmail/v1/users/me/threads/thread_2?format=full HTTP/1.1\n\n"
        f"--{boundary}--\n"
    )
    
    # Create a mock response object that simulates partial failure
    # The batch response will contain both 200 and non-200 responses
    mock_response = Mock()
    mock_response.raise_for_status = Mock()  # Overall batch request succeeds
    mock_response.headers = {"Content-Type": f"multipart/mixed; boundary={boundary}"}
    # Simulate batch response with one success (200) and one failure (404)
    mock_response.text = (
        f"--{boundary}\n"
        "Content-Type: application/http\n"
        "Content-ID: <response-1>\n\n"
        "HTTP/1.1 200 OK\n"
        "Content-Type: application/json\n\n"
        '{"id": "thread_1", "messages": []}\n'
        f"--{boundary}\n"
        "Content-Type: application/http\n"
        "Content-ID: <response-2>\n\n"
        "HTTP/1.1 404 Not Found\n"
        "Content-Type: application/json\n\n"
        '{"error": "Thread not found"}\n'
        f"--{boundary}--\n"
    )
    
    # Mock requests.post
    mock_post = mocker.patch("app.gmail_api.requests.post")
    mock_post.return_value = mock_response
    
    # Act
    result = batch_get_threads(access_token, headers, batch_body)
    
    # Assert
    assert result == mock_response
    
    # Verify requests.post was called with correct parameters
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args.kwargs["headers"] == headers
    assert call_args.kwargs["data"] == batch_body
    
    # Verify raise_for_status was called (batch request itself succeeded)
    mock_response.raise_for_status.assert_called_once()


def test_get_all_threads_success(mocker):
    """
    Test end-to-end flow with mocked batch response.
    """
    # Arrange
    access_token = "test_access_token_12345"
    max_threads = 2
    
    # Mock get_recent_thread_ids response
    mock_threads_data = {
        "threads": [
            {"id": "thread_1", "snippet": "Test email 1"},
            {"id": "thread_2", "snippet": "Test email 2"},
        ]
    }
    
    # Mock batch response
    boundary = "batch_1234567890"
    mock_batch_response = Mock()
    mock_batch_response.raise_for_status = Mock()
    mock_batch_response.headers = {"Content-Type": f"multipart/mixed; boundary={boundary}"}
    mock_batch_response.text = (
        f"--{boundary}\n"
        "Content-Type: application/http\n"
        "Content-ID: <response-1>\n\n"
        "HTTP/1.1 200 OK\n"
        "Content-Type: application/json\n\n"
        '{"id": "thread_1", "threadId": "thread_1", "messages": ['
        '{"id": "msg_1", "threadId": "thread_1", "snippet": "Test snippet 1", '
        '"payload": {"headers": [{"name": "From", "value": "sender1@example.com"}, '
        '{"name": "Subject", "value": "Test Subject 1"}]}}]}\n'
        f"--{boundary}\n"
        "Content-Type: application/http\n"
        "Content-ID: <response-2>\n\n"
        "HTTP/1.1 200 OK\n"
        "Content-Type: application/json\n\n"
        '{"id": "thread_2", "threadId": "thread_2", "messages": ['
        '{"id": "msg_2", "threadId": "thread_2", "snippet": "Test snippet 2", '
        '"payload": {"headers": [{"name": "From", "value": "sender2@example.com"}, '
        '{"name": "Subject", "value": "Test Subject 2"}]}}]}\n'
        f"--{boundary}--\n"
    )
    
    # Mock requests.get (for get_recent_thread_ids)
    mock_get_response = Mock()
    mock_get_response.json.return_value = mock_threads_data
    mock_get_response.raise_for_status = Mock()
    
    # Mock requests.post (for batch_get_threads)
    mock_post = mocker.patch("app.gmail_api.requests.post")
    mock_post.return_value = mock_batch_response
    
    mock_get = mocker.patch("app.gmail_api.requests.get")
    mock_get.return_value = mock_get_response
    
    # Act
    result = get_all_threads(access_token, max_threads)
    
    # Assert
    assert len(result) == 2
    assert result[0].id == "msg_1"
    assert result[0].thread_id == "thread_1"
    assert result[0].from_ == "sender1@example.com"
    assert result[0].subject == "Test Subject 1"
    assert result[1].id == "msg_2"
    assert result[1].thread_id == "thread_2"
    assert result[1].from_ == "sender2@example.com"
    assert result[1].subject == "Test Subject 2"
    
    # Verify get_recent_thread_ids was called with correct max_threads
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert call_args.kwargs["params"]["maxResults"] == max_threads
    
    # Verify batch_get_threads was called
    mock_post.assert_called_once()


def test_get_all_threads_max_threads_limit(mocker):
    """
    Test that max_threads parameter is respected.
    """
    # Arrange
    access_token = "test_access_token_12345"
    max_threads = 5
    
    # Mock get_recent_thread_ids response with exactly max_threads threads
    mock_threads_data = {
        "threads": [
            {"id": f"thread_{i}", "snippet": f"Test email {i}"}
            for i in range(1, max_threads + 1)
        ]
    }
    
    # Mock batch response (simplified - just need to verify max_threads is passed)
    boundary = "batch_1234567890"
    mock_batch_response = Mock()
    mock_batch_response.raise_for_status = Mock()
    mock_batch_response.headers = {"Content-Type": f"multipart/mixed; boundary={boundary}"}
    mock_batch_response.text = f"--{boundary}--\n"
    
    # Mock requests.get (for get_recent_thread_ids)
    mock_get_response = Mock()
    mock_get_response.json.return_value = mock_threads_data
    mock_get_response.raise_for_status = Mock()
    
    # Mock requests.post (for batch_get_threads)
    mock_post = mocker.patch("app.gmail_api.requests.post")
    mock_post.return_value = mock_batch_response
    
    mock_get = mocker.patch("app.gmail_api.requests.get")
    mock_get.return_value = mock_get_response
    
    # Act
    get_all_threads(access_token, max_threads)
    
    # Assert - Verify max_threads was passed to get_recent_thread_ids
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert call_args.kwargs["params"]["maxResults"] == max_threads
    
    # Verify batch_get_threads was called with batch_body containing max_threads requests
    mock_post.assert_called_once()
    batch_call_args = mock_post.call_args
    batch_body = batch_call_args.kwargs["data"]
    
    # Count the number of thread requests in the batch body
    thread_count = batch_body.count("GET /gmail/v1/users/me/threads/")
    assert thread_count == max_threads