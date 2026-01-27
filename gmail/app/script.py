import json
import os.path
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_access_token():
    # Get the project root directory (parent of gmail directory)
    current_dir = Path(__file__).parent
    project_root = current_dir.parent
    # Look for token.json in gmail-client/creds/token.json
    token_path = project_root / "gmail-client" / "creds" / "token.json"
    
    # Fallback to local token.json if the gmail-client one doesn't exist
    if not token_path.exists():
        token_path = current_dir / "token.json"
    
    with open(token_path, 'r') as f:
        data = json.load(f)
        
    return data['token']

def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  current_dir = Path(__file__).parent
  project_root = current_dir.parent
  token_path = project_root / "gmail-client" / "creds" / "token.json"
  
  if not token_path.exists():
    token_path = current_dir / "token.json"
  
  if os.path.exists(str(token_path)):
    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      credentials_path = project_root / "gmail-client" / "creds" / "credentials.json"
      if not credentials_path.exists():
        credentials_path = current_dir / "credentials.json"
      flow = InstalledAppFlow.from_client_secrets_file(
          str(credentials_path), SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(str(token_path), "w") as token:
      token.write(creds.to_json())

  try:
    # Call the Gmail API
    with open(str(token_path), 'r') as f:
        data  = json.load(f)
        
    token = data['token']
  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")

if __name__ == "__main__":
  main()