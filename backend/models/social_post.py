"""
Social Post Model - For social media content generation
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from backend.db.base import Base
import enum

class SocialPlatform(str, enum.Enum):
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"

class SocialPostStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"

class SocialPost(Base):
    __tablename__ = "social_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content_text = Column(Text, nullable=False)
    content_json = Column(Text, nullable=False)  # JSON with formatted content, hashtags, etc.
    
    # Platform
    platform = Column(Enum(SocialPlatform), nullable=False, index=True)
    status = Column(Enum(SocialPostStatus), default=SocialPostStatus.DRAFT, nullable=False)
    
    # Media
    image_url = Column(String(500), nullable=True)
    image_description = Column(Text, nullable=True)  # For AI image generation
    
    # Scheduling
    scheduled_for = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    hashtags = Column(String(500), nullable=True)  # Comma-separated
    
    # Organization
    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    
    # Analytics
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    views = Column(Integer, default=0)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # AI generation metadata
    ai_generated = Column(Boolean, default=False)
    generation_prompt = Column(Text, nullable=True)
