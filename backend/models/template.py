"""
Template model
"""

from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP, Text, ForeignKey, ARRAY, DECIMAL
from sqlalchemy.sql import func
from backend.db.base import Base
from backend.db.types import UUID, JSONB
import uuid


class Template(Base):
    __tablename__ = "templates"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    
    # Design
    theme_id = Column(UUID(), ForeignKey('themes.id'))
    preview_url = Column(Text)
    thumbnail_url = Column(Text)
    
    # Content structure
    content = Column(JSONB(), nullable=False)  # Default card layout
    num_cards = Column(Integer)
    card_types = Column(Text)  # Comma-separated list
    
    # Categorization
    category = Column(String(50))
    subcategory = Column(String(50))
    industry = Column(String(50))
    tags = Column(Text)  # Comma-separated
    
    # Stats
    usage_count = Column(Integer, default=0)
    rating = Column(DECIMAL(3, 2), default=0.0)
    rating_count = Column(Integer, default=0)
    
    # Custom template fields
    is_custom = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    created_by = Column(UUID(), ForeignKey('users.id'))
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Template(name='{self.name}', category='{self.category}')>"
