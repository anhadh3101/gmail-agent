import logging
from .gmail_api import get_all_threads
from .model import FetchRecentEmailsResponse

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("gmail")

logging.basicConfig(
    level=logging.INFO,
    format=f"%(asctime)s - %(levelname)s - %(message)s",
    filename="gmail_mcp_server.log",
    filemode="a"
)

logger = logging.getLogger(__name__)

@mcp.tool()
def fetch_recent_emails(access_token: str):
    """
    Fetches the recent emails from the user's inbox.
    
    Args:
        access_token: The access token for the user's Gmail API.
    """
    emails = get_all_threads(access_token, max_threads=20)
    
    logger.info(f"Fetched {len(emails)} emails")
    return FetchRecentEmailsResponse(
        emails=emails
    )
    
def main():
    logger.info("Starting Gmail MCP server")
    mcp.run(transport="stdio")
    logger.info("Gmail MCP server stopped")
    
if __name__ == "__main__":
    main()