from pydantic import BaseModel
from typing import List, Optional

class Tool(BaseModel):
    name: str
    description: str
    requires_auth: bool
    
class FetchRecentEmailsRequest(BaseModel):
    access_token: str
    
class EmailPreview(BaseModel):
    id: str
    thread_id: str
    snippet: str
    from_: Optional[str]
    subject: Optional[str]
    
class FetchRecentEmailsResponse(BaseModel):
    emails: List[EmailPreview]