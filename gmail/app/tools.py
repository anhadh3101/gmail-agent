from .model import Tool

AVAILABLE_TOOLS = [
    Tool(
        name="fetch_recent_emails",
        description="Fetch the emails recieved in the last 24 hours from the user's inbox.",
        requires_auth=True
    ),
]