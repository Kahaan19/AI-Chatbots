from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.database import get_db
from app.schemas.message import Message, MessageCreate
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService
from app.services.domain_service import DomainService
from app.services.ai_service import ai_service
from app.utils.dependencies import get_current_user
from app.models.user import User
from app.schemas.domain import Domain as DomainSchema
router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    user_message: Message
    ai_response: Message

@router.post("/{conversation_id}/stream")
async def stream_message(
    conversation_id: int,
    chat_request: ChatRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    length: str = "medium"  # "short", "medium", "long"
):
    """Send a message and stream AI response"""

    # Verify conversation belongs to user
    conversation = ConversationService.get_conversation_by_id(db, conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get domain information
    domain = DomainService.get_domain_by_id(db, conversation.domain_id)
    if not domain:
        raise HTTPException(status_code=400, detail="Invalid domain")
    
    domain_data= DomainSchema.from_orm(domain)

    # Create user message
    user_message_data = MessageCreate(
        conversation_id=conversation_id,
        role="user",
        content=chat_request.message
    )
    user_message = MessageService.create_message(db, user_message_data)

    # Get conversation history for context
    conversation_history = MessageService.get_conversation_history(db, conversation_id, limit=10)
    ai_response_buffer = []
    # Streaming generator for AI response
    async def event_generator():
        try:
            async for chunk in ai_service.stream_ai_response(
                domain=domain_data,
                message_content=chat_request.message,
                conversation_history=conversation_history,
                conversation_id=conversation_id,
                length=length
            ):
                ai_response_buffer.append(chunk)
                yield chunk
        except Exception as e:
            yield f"\n[Error]: {str(e)}"
        # Wait for the response to finish streaming
        full_ai_response = "".join(ai_response_buffer)
        print("AI response to save:", full_ai_response)
        if full_ai_response.strip():
            ai_message_data = MessageCreate(
                conversation_id=conversation_id,
                role="assistant",
                content=full_ai_response
            )
        MessageService.create_message(db, ai_message_data)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
  
@router.post("/{conversation_id}", response_model=ChatResponse)
def send_message(
    conversation_id: int,
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send a message and get AI response"""

    # Verify conversation belongs to user
    conversation = ConversationService.get_conversation_by_id(db, conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get domain information
    domain = DomainService.get_domain_by_id(db, conversation.domain_id)
    if not domain:
        raise HTTPException(status_code=400, detail="Invalid domain")
    domain_data = DomainSchema.from_orm(domain)
    # Create user message
    user_message_data = MessageCreate(
        conversation_id=conversation_id,
        role="user",
        content=chat_request.message
    )
    user_message = MessageService.create_message(db, user_message_data)

    # Get conversation history for context
    conversation_history = MessageService.get_conversation_history(db, conversation_id, limit=10)

    # Generate AI response
    ai_response_content = ai_service.generate_response(
        domain=domain_data,
        message_content=chat_request.message,
        conversation_history=conversation_history,
        conversation_id=conversation_id
    )

    # Create AI message
    ai_message_data = MessageCreate(
        conversation_id=conversation_id,
        role="assistant",
        content=ai_response_content
    )
    ai_message = MessageService.create_message(db, ai_message_data)

    return ChatResponse(
        user_message=user_message,
        ai_response=ai_message
    )

@router.get("/{conversation_id}/history", response_model=List[Message])
def get_chat_history(
    conversation_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get chat history for a conversation"""

    # Verify conversation belongs to user
    conversation = ConversationService.get_conversation_by_id(db, conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return MessageService.get_conversation_history(db, conversation_id, limit)