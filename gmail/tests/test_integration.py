import pytest
import os, json
from pathlib import Path
from unittest.mock import Mock
from app.gmail_api import get_all_threads
import dotenv

dotenv.load_dotenv()

PARENT_DIR = Path(__file__).parent
MOCK_THREADS_PATH = PARENT_DIR / "fixtures" / "mock_threads_response.json"
MOCK_BATCH_PATH = PARENT_DIR / "fixtures" / "mock_batch_response.json"

def test_get_all_threads_integration(mocker):
    """
    Test integration of get_all_threads function.
    """
    # Arrange
    access_token = "test_access_token_12345"
    max_threads = 30
    assert access_token is not None
    
    # Load the mock response from the API call
    thread_json = {}
    with open(MOCK_THREADS_PATH, 'r') as f:
        thread_json = json.load(f)
    
    batch_json = {}
    with open(MOCK_BATCH_PATH, 'r') as f:
        batch_json = json.load(f)
        
    # Mock the get_recent_thread_ids function
    mock_get_recent_thread_ids = mocker.patch("app.gmail_api.get_recent_thread_ids")
    mock_get_recent_thread_ids.return_value = thread_json["threads"]
    
    # Create a mock response object that mimics requests.Response
    mock_response = Mock()
    mock_response.headers = batch_json["headers"]
    mock_response.text = batch_json["response_text"]
    mock_response.raise_for_status = Mock()
    
    mock_batch_get_threads = mocker.patch("app.gmail_api.batch_get_threads")
    mock_batch_get_threads.return_value = mock_response
    
    # Act
    result = get_all_threads(access_token, max_threads)
    
    # Assert
    assert result is not None
    assert len(result) == len(batch_json["expected_emails"])
    
    # Verify each email matches expected structure
    for i, expected_email in enumerate(batch_json["expected_emails"]):
        assert result[i].id == expected_email["id"]
        assert result[i].thread_id == expected_email["thread_id"]
        assert result[i].snippet == expected_email["snippet"]
        assert result[i].from_ == expected_email["from_"]
        assert result[i].subject == expected_email["subject"]
    