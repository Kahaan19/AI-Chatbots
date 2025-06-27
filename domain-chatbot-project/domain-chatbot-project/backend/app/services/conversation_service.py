from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.models.user import User
from app.schemas.conversation import ConversationCreate, ConversationUpdate
from typing import List, Optional

class ConversationService:
    @staticmethod
    def create_conversation(db: Session, conversation: ConversationCreate, user_id: int) -> Conversation:
        # Generate title if not provided
        title = conversation.title or f"New {conversation.domain_id} conversation"
        
        db_conversation = Conversation(
            user_id=user_id,
            domain_id=conversation.domain_id,
            title=title
        )
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
        return db_conversation
    
    @staticmethod
    def get_user_conversations(db: Session, user_id: int, domain_id: Optional[int] = None) -> List[Conversation]:
        query = db.query(Conversation).filter(Conversation.user_id == user_id)
        if domain_id:
            query = query.filter(Conversation.domain_id == domain_id)
        return query.order_by(Conversation.updated_at.desc()).all()
    
    @staticmethod
    def get_conversation_by_id(db: Session, conversation_id: int, user_id: int) -> Optional[Conversation]:
        return db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
    
    @staticmethod
    def update_conversation(db: Session, conversation_id: int, user_id: int, update_data: ConversationUpdate) -> Optional[Conversation]:
        conversation = ConversationService.get_conversation_by_id(db, conversation_id, user_id)
        if not conversation:
            return None
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(conversation, field, value)
        
        db.commit()
        db.refresh(conversation)
        return conversation
    
    @staticmethod
    def delete_conversation(db: Session, conversation_id: int, user_id: int) -> bool:
        conversation = ConversationService.get_conversation_by_id(db, conversation_id, user_id)
        if not conversation:
            return False
        
        db.delete(conversation)
        db.commit()
        return True