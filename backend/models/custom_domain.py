"""
Custom Domain Model - For Pro/Ultra users to publish webpages on their own domains
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from backend.db.base import Base
import enum

class DomainStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"

class CustomDomain(Base):
    __tablename__ = "custom_domains"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), unique=True, nullable=False, index=True)
    
    # Owner
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Verification
    status = Column(Enum(DomainStatus), default=DomainStatus.PENDING, nullable=False)
    verification_code = Column(String(100), nullable=True)
    verification_method = Column(String(50), nullable=True)  # "dns", "file"
    
    # DNS Records
    dns_records = Column(Text, nullable=True)  # JSON with required DNS records
    
    # SSL Certificate
    ssl_enabled = Column(Boolean, default=False)
    ssl_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Usage
    is_active = Column(Boolean, default=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)
