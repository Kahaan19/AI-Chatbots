from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from .domain import Domain
from .message import Message
class ConversationBase(BaseModel):
    title: Optional[str] = None
    domain_id: int

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(BaseModel):
    title: Optional[str] = None

class Conversation(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    domain: Optional[Domain] = None
    
    class Config:
        from_attributes = True

class ConversationWithMessages(Conversation):
    messages: List[Message] = []