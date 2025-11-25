"""
Theme model
"""

from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP, Text, ForeignKey, ARRAY
from sqlalchemy.sql import func
from backend.db.base import Base
from backend.db.types import UUID, JSONB
import uuid


class Theme(Base):
    __tablename__ = "themes"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    
    # Colors
    colors = Column(JSONB(), nullable=False)  # primary, secondary, accent, background, text
    
    # Typography
    fonts = Column(JSONB(), nullable=False)  # heading, body, code
    font_sizes = Column(JSONB())
    
    # Layout
    spacing = Column(JSONB())
    border_radius = Column(String(50))
    
    # Custom theme fields
    created_by = Column(UUID(), ForeignKey('users.id'))
    workspace_id = Column(UUID(), ForeignKey('workspaces.id'))
    is_custom = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    
    # Categorization
    category = Column(String(50))
    tags = Column(Text)
    
    # Preview
    preview_url = Column(Text)
    thumbnail_url = Column(Text)
    
    # Stats
    usage_count = Column(Integer, default=0)
    rating = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Theme(name='{self.name}', category='{self.category}')>"
