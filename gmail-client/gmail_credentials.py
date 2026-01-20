import json
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

TOKEN_PATH = "creds/token.json"
CREDENTIALS_PATH = "creds/credentials.json"

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_access_token():
    """
    OAuth flow to get the access token for the Gmail API.
    
    Raises:
        FileNotFoundError: If the credentials file is not found.
        HttpError: If an error occurs with the Gmail API.
        
    Returns:
        str: The access token for the Gmail API.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    
    # Check if the user provided GCP credentials file or not.
    if not os.path.exists(CREDENTIALS_PATH):
        raise FileNotFoundError("Credentials not found on path: " + CREDENTIALS_PATH)
    
    # Check if the user has a token generated or not.
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    try:
    # Call the Gmail API
        with open(TOKEN_PATH, 'r') as f:
            data  = json.load(f)
        
        token = data['token']
        return token
    except HttpError as error:
        raise HttpError(f"An error occurred with the Gmail API: {error}")
    
# Main entry point to test the function
if __name__ == "__main__":
    print(get_access_token())
