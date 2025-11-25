"""
Document Model - For long-form content (reports, articles, proposals, etc.)
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from backend.db.base import Base
import enum

class DocumentType(str, enum.Enum):
    REPORT = "report"
    ARTICLE = "article"
    PROPOSAL = "proposal"
    WHITEPAPER = "whitepaper"
    BLOG = "blog"
    MEMO = "memo"
    CASE_STUDY = "case_study"

class DocumentStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    subtitle = Column(String(1000), nullable=True)
    content_json = Column(Text, nullable=False)  # JSON structure with sections, paragraphs, images
    
    # Document type
    document_type = Column(Enum(DocumentType), nullable=False, default=DocumentType.ARTICLE)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT, nullable=False)
    
    # Theming
    theme_id = Column(Integer, ForeignKey("themes.id"), nullable=True)
    
    # Branding
    custom_branding = Column(Text, nullable=True)  # JSON with logo, colors, fonts
    
    # Metadata
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    word_count = Column(Integer, default=0)
    reading_time_minutes = Column(Integer, default=0)
    
    # Organization
    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    
    # Sharing
    is_public = Column(Boolean, default=False)
    public_slug = Column(String(100), unique=True, nullable=True, index=True)
    
    # Collaboration
    allow_comments = Column(Boolean, default=True)
    allow_exports = Column(Boolean, default=True)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # AI generation metadata
    ai_generated = Column(Boolean, default=False)
    generation_prompt = Column(Text, nullable=True)
