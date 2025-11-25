"""
Comment model for presentation collaboration
"""

from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.db.base import Base
from backend.db.types import UUID
import uuid


class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    presentation_id = Column(UUID(), ForeignKey("presentations.id", ondelete="CASCADE"), nullable=False, index=True)
    card_id = Column(String(50), nullable=True)  # Optional: specific card in presentation
    user_id = Column(UUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Comment content
    text = Column(Text, nullable=False)
    
    # Optional reply to another comment
    parent_id = Column(UUID(), ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    
    # Status
    is_resolved = Column(Integer, default=0)
    resolved_by = Column(UUID(), nullable=True)
    resolved_at = Column(TIMESTAMP, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Comment(presentation_id='{self.presentation_id}', user_id='{self.user_id}')>"


class SharedPresentation(Base):
    """Track presentations shared with other users"""
    __tablename__ = "shared_presentations"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    presentation_id = Column(UUID(), ForeignKey("presentations.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id = Column(UUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    shared_with_id = Column(UUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Permission level
    permission = Column(String(20), default="viewer")  # viewer, commenter, editor
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    expires_at = Column(TIMESTAMP, nullable=True)
    
    def __repr__(self):
        return f"<SharedPresentation(presentation_id='{self.presentation_id}', permission='{self.permission}')>"
