import os.path, json

import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Any
from datetime import datetime, timedelta

try:
    # Try relative import first (when run as part of package)
    from .user_ops import get_user_token, store_user_token, check_if_user_exists, store_user
except ImportError:
    # Fall back to mock functions when run as script
    def get_user_token(email: str):
        return None
    def store_user_token(email: str, token_json):
        pass
    def check_if_user_exists(email: str):
        return False
    def store_user(email: str, username: str):
        pass

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
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'openid',
    ]
    
    def __init__(self, email: str, credentials_file: str = None):
        """
        Initialize Gmail API client.
        
        Args:
            email: User's email address (used to fetch/store tokens in database)
            credentials_file: Path to OAuth2 credentials JSON file
        """
        self.email = email
        # Default to looking in the parent directory (backend folder)
        self.credentials_file = "credentials.json"
        self.service = None
        self.credentials = None
        
    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth2.
        Loads token from database if available, otherwise performs OAuth flow.
        
        Args:
            username: Optional username to save when creating new user
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            self.credentials = None
            
            # Try to load token from database
            token_data = get_user_token(self.email)
            
            # If token data is found, assign them to the credentials object
            if token_data:
                try:
                    # Load credentials from database token JSON
                    self.credentials = Credentials.from_authorized_user_info(
                        token_data,
                        self.SCOPES
                    )
                    print(f"[GmailAPI] Loaded credentials from database for {self.email}")
                except Exception as e:
                    print(f"[GmailAPI] Error loading credentials from database: {e}")
                    self.credentials = None
            
            # Check if credentials are valid or need refresh
            if self.credentials:
                if not self.credentials.valid:
                    if self.credentials.expired and self.credentials.refresh_token:
                        try:
                            print(f"[GmailAPI] Refreshing expired token for {self.email}")
                            self.credentials.refresh(Request())
                            
                            # Save refreshed token to database
                            token_data = json.loads(self.credentials.to_json())
                            store_user_token(
                                email=self.email,
                                token_json=token_data
                            )
                            print(f"[GmailAPI] Token refreshed and saved to database")
                        except Exception as e:
                            print(f"[GmailAPI] Token refresh failed: {e}")
                            self.credentials = None
            
            # If no valid credentials, perform OAuth flow
            if not self.credentials:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Gmail credentials file not found: {self.credentials_file}"
                    )
                
                print(f"[GmailAPI] Starting OAuth flow for {self.email}")
                # 
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, 
                    self.SCOPES
                )
                self.credentials = flow.run_local_server(port=0)
                
                # Save new token to database
                token_data = json.loads(self.credentials.to_json())
                store_user_token(
                    email=self.email,
                    token_json=token_data
                )
                print(f"[GmailAPI] New token saved to database for {self.email}")
            
            # Build Gmail service
            self.service = build("gmail", "v1", credentials=self.credentials)
            print(f"[GmailAPI] Authentication successful for {self.email}")
            return True
            
        except Exception as e:
            print(f"[GmailAPI] Authentication failed: {e}")
            return False
        
    def get_emails(self) -> List[Dict[str, Any]]:
        """
        Fetch all Gmail labels for the authenticated user.
        
        Returns:
            List[Dict]: List of label dictionaries
        """
        if not self.service:
            raise Exception("Not authenticated. Call authenticate() first.")
        
        # Use a hardcoded date for testing (last 7 days)
        # Format: YYYY/MM/DD
        last_fetched_time = (datetime.now() - timedelta(days=7)).strftime('%Y/%m/%d')
        current_time = datetime.now().strftime('%Y/%m/%d')
        
        # Construct the query to get the emails sent after the last fetched time.
        query = f"in:inbox after:{last_fetched_time} before:{current_time}"
        
        try:
            all_threads = []
            page_token = None
            
            # Loop through all pages of results
            while True:
                results = (
                    self.service.users().threads().list(
                        userId="me", 
                        q=query,
                        pageToken=page_token
                    ).execute()
                )
                
                print(f"[GmailAPI] Results: {results}")
                # Get threads from current page
                threads = results.get('threads', [])
                all_threads.extend(threads)
                
                # Check if there are more pages
                page_token = results.get('nextPageToken')
                if not page_token:
                    # No more pages, break out of loop
                    break
            
            print(f"[GmailAPI] Fetched {len(all_threads)} threads across all pages")
            return all_threads
            
        except HttpError as error:
            raise Exception(f"Failed to fetch emails: {error}")
    
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
    print()
    
    # Get user email
    email = input("Enter your Gmail address: ").strip()
    if not email:
        print("Email is required!")
        return
    
    # Initialize Gmail API with user's email
    gmail_api = GmailAPI(email=email)
    
    # Authenticate
    print(f"\nAuthenticating {email} with Gmail...")
    if not gmail_api.authenticate():
        print("Failed to authenticate with Gmail API.")
        return
    
    print("\n✓ Authentication successful!")
    print()
    
    # Fetch and display threads
    threads = gmail_api.get_emails()
    print(f"Fetched {len(threads)} threads")
    
    for thread in threads[:5]:  # Show first 5 threads only
        print(f"\nThread ID: {thread['id']}")

if __name__ == "__main__":
    main()
