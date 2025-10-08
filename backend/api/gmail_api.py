import os.path

import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Any
    
CLIENTSECRETS_LOCATION = '/gmail-agent/credentials.json'
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    # Add other requested scopes.
]

class GmailAPI:
    """
    Gmail API wrapper class for authentication and basic operations.
    
    This class handles:
    - OAuth2 authentication with Gmail
    - Fetching Gmail labels
    - Basic Gmail API operations
    """
    
    # If modifying these scopes, delete the file token.json.
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly'
        # Add other requested scopes.
    ]
    
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.json"):
        """
        Initialize Gmail API client.
        
        Args:
            credentials_file: Path to OAuth2 credentials JSON file
            token_file: Path to store/load access tokens
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.credentials = None
        
    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth2.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            self.credentials = None
            
            # Load existing credentials
            if os.path.exists(self.token_file):
                self.credentials = Credentials.from_authorized_user_file(
                    self.token_file, 
                    self.SCOPES
                )
            
            # If no valid credentials available, authenticate
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        raise FileNotFoundError(
                            f"Gmail credentials file not found: {self.credentials_file}"
                        )
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, 
                        self.SCOPES
                    )
                    self.credentials = flow.run_local_server(port=0)
                    print(self.credentials.to_json())
                
                # Save credentials for the next run
                with open(self.token_file, "w") as token:
                    token.write(self.credentials.to_json())
            
            # Build Gmail service
            self.service = build("gmail", "v1", credentials=self.credentials)
            return True
            
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    def get_labels(self) -> List[Dict[str, Any]]:
        """
        Fetch all Gmail labels for the authenticated user.
        
        Returns:
            List[Dict]: List of label dictionaries
        """
        if not self.service:
            raise Exception("Not authenticated. Call authenticate() first.")
        
        try:
            results = self.service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])
            return labels
            
        except HttpError as error:
            raise Exception(f"Failed to fetch labels: {error}")
    
    def print_labels(self) -> None:
        """
        Print all Gmail labels to console.
        """
        try:
            labels = self.get_labels()
            
            if not labels:
                print("No labels found.")
                return
            
            print("Gmail Labels:")
            print("-" * 50)
            for label in labels:
                print(f"• {label['name']}")
                
        except Exception as error:
            print(f"An error occurred while fetching labels: {error}")
    
    def is_authenticated(self) -> bool:
        """
        Check if the API is authenticated.
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        return self.service is not None
    
    def get_service(self):
        """
        Get the Gmail service object.
        
        Returns:
            Gmail service object or None if not authenticated
        """
        return self.service


def main():
    """
    Main function to demonstrate Gmail API usage.
    Shows basic usage of the Gmail API by listing user's Gmail labels.
    """
    print("Gmail Agent - API Demo")
    print("=" * 50)
    
    # Initialize Gmail API
    gmail_api = GmailAPI()
    
    # Authenticate
    print("Authenticating with Gmail...")
    if not gmail_api.authenticate():
        print("Failed to authenticate with Gmail API.")
        return
    
    print("✓ Authentication successful!")
    print()
    
    # Fetch and display labels
    gmail_api.print_labels()


if __name__ == "__main__":
    main()
