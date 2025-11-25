"""
Presentation model
"""

from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.db.base import Base
from backend.db.types import UUID, JSONB
import uuid


class Presentation(Base):
    __tablename__ = "presentations"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    slug = Column(String(255), unique=True)
    
    # Ownership
    workspace_id = Column(UUID(), ForeignKey('workspaces.id', ondelete='CASCADE'))
    owner_id = Column(UUID(), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Content
    content = Column(JSONB(), nullable=False, default={'cards': []})
    
    # Theme & design
    theme_id = Column(UUID())
    custom_theme = Column(JSONB())
    
    # Settings
    is_public = Column(Boolean, default=False)
    is_published = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    password_protected = Column(Boolean, default=False)
    password_hash = Column(String(255))
    
    # Sharing
    public_url = Column(String(255), unique=True)
    embed_code = Column(Text)
    allow_comments = Column(Boolean, default=True)
    allow_downloads = Column(Boolean, default=True)
    
    # Analytics
    view_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    published_at = Column(TIMESTAMP)
    archived_at = Column(TIMESTAMP)
    deleted_at = Column(TIMESTAMP)
    
    # Metadata
    description = Column(Text)
    tags = Column(Text)  # Comma-separated
    thumbnail_url = Column(Text)
    
    # Version control
    version = Column(Integer, default=1)
    parent_version_id = Column(UUID())
    
    def __repr__(self):
        return f"<Presentation(title='{self.title}', id='{self.id}')>"
