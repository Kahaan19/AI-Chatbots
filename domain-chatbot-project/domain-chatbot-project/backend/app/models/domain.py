# app/models/domain.py
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Domain(Base):
    """
    Domain model represents the different chat domains available
    (stock, law, entertainment, psychology, technical)
    """
    __tablename__ = "domains"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Domain information
    name = Column(String(50), unique=True, nullable=False, index=True)  # e.g., "stock", "law"
    description = Column(Text, nullable=True)  # Human-readable description
    system_prompt = Column(Text, nullable=False)  # The prompt that defines the AI's behavior in this domain
    
    # Relationships
    # One domain can have many conversations
    conversations = relationship("Conversation", back_populates="domain")
    
    def __repr__(self):
        return f"<Domain(id={self.id}, name='{self.name}')>"

# Why we need a separate Domain table:
# 1. Centralized domain management - easy to add/modify domains
# 2. Each domain can have its own system prompt for AI behavior
# 3. We can track usage statistics per domain
# 4. Easier to maintain and scale different domain types