"""
Configuration settings for Gmail Agent application.
"""

import os
from typing import List

class Config:
    """Base configuration class"""
    
    # Gmail API Configuration
    GMAIL_CREDENTIALS_FILE: str = "credentials.json"
    GMAIL_TOKEN_FILE: str = "token.json"
    GMAIL_SCOPES: List[str] = ["https://www.googleapis.com/auth/gmail.readonly"]
    
    # Application Settings
    DEBUG: bool = True
    PORT: int = 5000
    
    # Email Processing Settings
    EMAIL_FETCH_LIMIT: int = 50
    EMAIL_TIME_WINDOW_HOURS: int = 24
    
    # LangChain Configuration (for future AI integration)
    OPENAI_API_KEY: str = os.environ.get('OPENAI_API_KEY', '')
    
    @classmethod
    def get_credentials_file(cls) -> str:
        """Get the path to Gmail credentials file"""
        return cls.GMAIL_CREDENTIALS_FILE
    
    @classmethod
    def get_token_file(cls) -> str:
        """Get the path to Gmail token file"""
        return cls.GMAIL_TOKEN_FILE
    
    @classmethod
    def get_scopes(cls) -> List[str]:
        """Get Gmail API scopes"""
        return cls.GMAIL_SCOPES.copy()
