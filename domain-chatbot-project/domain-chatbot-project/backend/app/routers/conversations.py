from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.conversation import Conversation, ConversationCreate, ConversationUpdate
from app.services.conversation_service import ConversationService
from app.services.domain_service import DomainService
from app.utils.dependencies import get_current_user
from app.models.user import User
from app.schemas.conversation import ConversationWithMessages
from app.services.message_service import MessageService

router = APIRouter(prefix="/conversations", tags=["conversations"])
@router.get("/{conversation_id}/messages", response_model=ConversationWithMessages)
def get_conversation_with_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get conversation with all messages"""
    conversation = ConversationService.get_conversation_by_id(db, conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = MessageService.get_conversation_messages(db, conversation_id)
    conversation_dict = {
        **conversation.__dict__,
        "messages": messages
    }
    return ConversationWithMessages(**conversation_dict)
@router.post("/", response_model=Conversation)
def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new conversation"""
    # Validate domain exists
    domain = DomainService.get_domain_by_id(db, conversation.domain_id)
    if not domain:
        raise HTTPException(status_code=400, detail="Invalid domain ID")
    
    return ConversationService.create_conversation(db, conversation, current_user.id)

@router.get("/", response_model=List[Conversation])
def get_conversations(
    domain_id: Optional[int] = Query(None, description="Filter by domain ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's conversations, optionally filtered by domain"""
    return ConversationService.get_user_conversations(db, current_user.id, domain_id)

@router.get("/{conversation_id}", response_model=Conversation)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific conversation"""
    conversation = ConversationService.get_conversation_by_id(db, conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@router.put("/{conversation_id}", response_model=Conversation)
def update_conversation(
    conversation_id: int,
    update_data: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update conversation (mainly title)"""
    conversation = ConversationService.update_conversation(db, conversation_id, current_user.id, update_data)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete conversation"""
    success = ConversationService.delete_conversation(db, conversation_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted successfully"}