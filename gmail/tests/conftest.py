# conftest.py
import pytest

pytest_plugins = ["pytest_mock"]


@pytest.fixture
def mock_access_token():
    """
    Fixture providing a mock access token.
    """
    return "test_access_token_12345"