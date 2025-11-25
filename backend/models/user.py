"""
User model
"""

from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP, Text
from sqlalchemy.sql import func
from backend.db.base import Base
from backend.db.types import UUID, JSONB
import uuid


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255))
    name = Column(String(255))
    avatar_url = Column(Text)
    
    # OAuth
    google_id = Column(String(255), unique=True)
    microsoft_id = Column(String(255), unique=True)
    oauth_provider = Column(String(50))
    
    # Subscription
    plan = Column(String(20), default='free')
    credits_remaining = Column(Integer, default=400)
    credits_reset_date = Column(TIMESTAMP)
    subscription_id = Column(String(255))
    subscription_status = Column(String(50))
    stripe_customer_id = Column(String(255))
    
    # Preferences
    language = Column(String(10), default='en')
    timezone = Column(String(50))
    default_theme_id = Column(UUID())
    settings = Column(JSONB())
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    last_login = Column(TIMESTAMP)
    
    # Usage tracking
    total_presentations = Column(Integer, default=0)
    total_ai_generations = Column(Integer, default=0)
    credits_used = Column(Integer, default=0)
    exports_this_month = Column(Integer, default=0)
    
    def has_credits(self, cost: int) -> bool:
        """Check if user has enough credits for operation"""
        # Unlimited credits for paid plans
        if self.plan in ['plus', 'pro', 'ultra', 'team', 'business']:
            return True
        # Check credits for free plan
        return self.credits_remaining >= cost
    
    def deduct_credits(self, cost: int) -> bool:
        """Deduct credits from user account"""
        # Unlimited credits for paid plans
        if self.plan in ['plus', 'pro', 'ultra', 'team', 'business']:
            return True
        
        # Deduct for free plan
        if self.credits_remaining >= cost:
            self.credits_remaining -= cost
            self.credits_used += cost
            return True
        return False
    
    def can_export(self) -> bool:
        """Check if user can export presentations"""
        if self.plan == 'free':
            return False
        return True
    
    def has_feature(self, feature: str) -> bool:
        """Check if user has access to a feature"""
        from backend.config import settings
        
        if self.plan == 'free':
            return feature in settings.FREE_FEATURES
        elif self.plan == 'plus':
            return feature in settings.PLUS_FEATURES
        elif self.plan in ['pro', 'ultra', 'team', 'business']:
            return feature in settings.PRO_FEATURES
        
        return False
    
    def get_max_cards(self) -> int:
        """Get maximum cards per generation for user's plan"""
        from backend.config import PLAN_CONFIGS
        
        plan_config = PLAN_CONFIGS.get(self.plan, PLAN_CONFIGS['free'])
        return plan_config.get('max_cards_per_generation', 10)
    
    def __repr__(self):
        return f"<User(email='{self.email}', plan='{self.plan}')>"
