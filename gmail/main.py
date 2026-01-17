from fastapi import FastAPI
from typing import List
import logging
from model import Tool, FetchRecentEmailsRequest, FetchRecentEmailsResponse
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

def main():
    print("Hello from gmail!")


if __name__ == "__main__":
    main()
