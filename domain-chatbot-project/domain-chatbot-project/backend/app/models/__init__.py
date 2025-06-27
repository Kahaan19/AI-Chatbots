# app/models/__init__.py
"""
This file makes the models directory a Python package and 
imports all our models so they can be easily imported elsewhere.
"""

from .user import User
from .domain import Domain
from .conversation import Conversation
from .message import Message

# Export all models
__all__ = ["User", "Domain", "Conversation", "Message"]

# Why this approach?
# 1. Clean imports: `from app.models import User` instead of `from app.models.user import User`
# 2. Central place to manage all model imports
# 3. Makes it clear what models are available in this package