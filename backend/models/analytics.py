"""
Analytics model for tracking user activity and usage
"""

from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey, Float
from sqlalchemy.sql import func
from backend.db.base import Base
from backend.db.types import UUID, JSONB
import uuid


class Analytics(Base):
    """Track detailed analytics events"""
    __tablename__ = "analytics"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Event details
    event_type = Column(String(50), nullable=False, index=True)  # generation, export, view, edit, etc.
    event_category = Column(String(50), nullable=True)
    event_action = Column(String(100), nullable=True)
    
    # Related resources
    presentation_id = Column(UUID(), nullable=True, index=True)
    template_id = Column(UUID(), nullable=True)
    theme_id = Column(UUID(), nullable=True)
    
    # Event metadata (renamed from metadata to avoid SQLAlchemy reserved name)
    event_metadata = Column(JSONB(), nullable=True)
    
    # Credits used
    credits_used = Column(Integer, default=0)
    
    # Timing
    duration_ms = Column(Integer, nullable=True)  # Duration of operation in milliseconds
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<Analytics(event_type='{self.event_type}', user_id='{self.user_id}')>"


class PresentationView(Base):
    """Track presentation views"""
    __tablename__ = "presentation_views"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    presentation_id = Column(UUID(), ForeignKey("presentations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Viewer info
    viewer_id = Column(UUID(), nullable=True)  # NULL if anonymous
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    referrer = Column(String(255), nullable=True)
    
    # Location
    country = Column(String(2), nullable=True)
    city = Column(String(100), nullable=True)
    
    # Engagement
    time_spent_seconds = Column(Integer, nullable=True)
    cards_viewed = Column(Integer, nullable=True)
    
    # Timestamps
    viewed_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<PresentationView(presentation_id='{self.presentation_id}')>"


class AggregatedStats(Base):
    """Pre-aggregated statistics for performance"""
    __tablename__ = "aggregated_stats"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Period
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    period_start = Column(TIMESTAMP, nullable=False, index=True)
    period_end = Column(TIMESTAMP, nullable=False)
    
    # Metrics
    presentations_created = Column(Integer, default=0)
    presentations_edited = Column(Integer, default=0)
    ai_generations = Column(Integer, default=0)
    credits_used = Column(Integer, default=0)
    exports_created = Column(Integer, default=0)
    views_received = Column(Integer, default=0)
    
    # Updated
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<AggregatedStats(user_id='{self.user_id}', period='{self.period_type}')>"
