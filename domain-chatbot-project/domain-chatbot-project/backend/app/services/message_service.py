from sqlalchemy.orm import Session
from app.models.message import Message
from app.models.conversation import Conversation
from app.schemas.message import MessageCreate
from typing import List, Optional

class MessageService:
    @staticmethod
    def create_message(db: Session, message: MessageCreate) -> Message:
        db_message = Message(**message.dict())
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        
        # Update conversation's updated_at timestamp
        conversation = db.query(Conversation).filter(Conversation.id == message.conversation_id).first()
        if conversation:
            conversation.updated_at = db_message.created_at
            db.commit()
        
        return db_message
    
    @staticmethod
    def get_conversation_messages(db: Session, conversation_id: int) -> List[Message]:
        return db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).all()
    
    @staticmethod
    def get_conversation_history(db: Session, conversation_id: int, limit: Optional[int] = None) -> List[Message]:
        query = db.query(Message).filter(Message.conversation_id == conversation_id)
        if limit:
            query = query.order_by(Message.created_at.desc()).limit(limit)
            messages = query.all()
            return list(reversed(messages))  # Return in chronological order
        return query.order_by(Message.created_at.asc()).all()