"""
Webpage Model - For public-facing web pages with custom domains
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from backend.db.base import Base
import enum

class WebpageType(str, enum.Enum):
    LANDING_PAGE = "landing_page"
    PORTFOLIO = "portfolio"
    ABOUT = "about"
    PRODUCT = "product"
    SERVICE = "service"
    EVENT = "event"
    BLOG_POST = "blog_post"

class WebpageStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class Webpage(Base):
    __tablename__ = "webpages"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    meta_description = Column(String(500), nullable=True)
    content_json = Column(Text, nullable=False)  # JSON structure with sections, hero, CTA, forms
    
    # Webpage type
    webpage_type = Column(Enum(WebpageType), nullable=False, default=WebpageType.LANDING_PAGE)
    status = Column(Enum(WebpageStatus), default=WebpageStatus.DRAFT, nullable=False)
    
    # Theming
    theme_id = Column(Integer, ForeignKey("themes.id"), nullable=True)
    
    # Custom domain & publishing
    custom_domain_id = Column(Integer, ForeignKey("custom_domains.id"), nullable=True)
    subdomain = Column(String(100), nullable=True, index=True)  # e.g., "mysite" -> mysite.gamma.app
    full_url = Column(String(500), nullable=True)  # e.g., https://mysite.gamma.app or https://custom.com
    
    # SEO
    seo_keywords = Column(String(1000), nullable=True)
    og_image_url = Column(String(500), nullable=True)  # Open Graph image
    
    # Branding
    favicon_url = Column(String(500), nullable=True)
    custom_header_html = Column(Text, nullable=True)
    custom_footer_html = Column(Text, nullable=True)
    
    # Metadata
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Organization
    folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    
    # Analytics
    view_count = Column(Integer, default=0)
    unique_visitors = Column(Integer, default=0)
    
    # Collaboration
    allow_comments = Column(Boolean, default=False)  # Usually false for public webpages
    
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
