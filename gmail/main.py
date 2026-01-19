from fastapi import FastAPI, Header, HTTPException
from typing import List, Optional
import logging
from gmail_api import get_all_threads
from script import get_access_token
from model import Tool, FetchRecentEmailsResponse, EmailPreview
from tools import AVAILABLE_TOOLS

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format=f"%(asctime)s - %(levelname)s - %(message)s",
    filename="gmail_mcp_server.log",
    filemode="a"
)

logger = logging.getLogger(__name__)

@app.get("/tools", response_model=List[Tool])
def get_tools():
    """
    Returns the available tools supported by this MCP server.
    """
    logger.info("Getting available tools\n")
    return AVAILABLE_TOOLS

@app.get("/fetch_recent_emails", response_model=FetchRecentEmailsResponse)
def fetch_recent_emails(
    authorization: Optional[str] = Header(None)
    ):
    """
    Fetches the recent emails from the user's inbox.
    """
    # If no authorization header is provided, return an error
    # if not authorization:
    #     raise HTTPException(status_code=400, detail="Authorization header required")
    
    # If the authorization header is not in the correct format, return an error
    # parts = authorization.split(" ")
    # if len(parts) != 2 or parts[0] != "Bearer":
    #     raise HTTPException(status_code=400, detail="Invalid authorization header")
    
    # Get the access token from the authorization header
    # access_token = parts[1]
    
    access_token = get_access_token()
    
    # TODO: Fetch the recent emails from the user's inbox using the access token
    emails = get_all_threads(access_token, max_threads=20)
    
    return FetchRecentEmailsResponse(
        emails=emails
    )