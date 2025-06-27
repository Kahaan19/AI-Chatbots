from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"))
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Add constraint to ensure role is either 'user' or 'assistant'
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name="check_role"),
    )
    
    # Relationship
    conversation = relationship("Conversation", back_populates="messages")