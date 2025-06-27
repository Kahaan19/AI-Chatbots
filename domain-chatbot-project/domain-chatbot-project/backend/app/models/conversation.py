# app/models/conversation.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class Conversation(Base):
    """
    Conversation model represents individual chat conversations
    Each conversation belongs to a user and a domain
    """
    __tablename__ = "conversations"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys - links to other tables
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False, index=True)
    
    # Conversation metadata
    title = Column(String(255), nullable=True)  # Optional title for the conversation
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    # Many conversations belong to one user
    user = relationship("User", back_populates="conversations")
    # Many conversations belong to one domain
    domain = relationship("Domain", back_populates="conversations")
    # One conversation can have many messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id}, domain_id={self.domain_id}, title='{self.title}')>"

# Database relationship concepts:
# 1. ForeignKey: Creates a link to another table's primary key
# 2. Many-to-One: Many conversations belong to one user/domain
# 3. One-to-Many: One conversation has many messages
# 4. index=True on foreign keys: Improves query performance