"""
Gmail Agent - Main Application Entry Point

Desktop application to run in background for fetching all emails.

1. Make desktop credentials on GCP and fix any configuration issues.
2. Get the APIs to develop the workflow for the app.
3. Develop the workflow to get the emails that were received in the last 24 hours or till some pivot point.
4. Figure out things we are going to configure on LangChain. (That is going to be the AI interface where emails are handled)
5. The flask app will help manage the information.

Need to build a frontend interface for getting the data.
"""

from flask import Flask, request
from logger.logger import setup_logger

from api.gmail_api import GmailAPI
from config import Config

app = Flask(__name__)
logger = setup_logger(__name__)

@app.route("/")
def home():
    logger.info("Home route hit by %s", request.remote_addr)
    return "Hello, Flask logging!"

@app.route("/error")
def trigger_error():
    try:
        1 / 0
    except Exception as e:
        logger.error("Error occurred: %s", e, exc_info=True)
        return "Something went wrong", 500

if __name__ == "__main__":
    app.run(debug=True)
    
def main():
    """
    Main application entry point.
    Demonstrates Gmail API integration and fetches user labels.
    """
    print("Gmail Agent - Main Application")
    print("=" * 50)
    
    # Initialize Gmail API with configuration
    gmail_api = GmailAPI(
        credentials_file=Config.get_credentials_file(),
        token_file=Config.get_token_file()
    )
    
    # Authenticate and fetch labels
    try:
        if gmail_api.authenticate():
            print("✓ Successfully authenticated with Gmail API")
            gmail_api.print_labels()
        else:
            print("✗ Failed to authenticate with Gmail API")
    except Exception as e:
        print(f"✗ Error: {e}")