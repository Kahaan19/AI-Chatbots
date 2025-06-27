from pydantic import BaseModel, validator
from datetime import datetime
from typing import Literal

class MessageBase(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class MessageCreate(MessageBase):
    conversation_id: int

class Message(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Update conversation schema to include messages
# Add this to app/schemas/conversation.py
from .message import Message