"""
Billing and payment history model
"""

from sqlalchemy import Column, String, Integer, TIMESTAMP, ForeignKey, Float, Boolean
from sqlalchemy.sql import func
from backend.db.base import Base
from backend.db.types import UUID, JSONB
import uuid


class BillingHistory(Base):
    """Track all billing transactions"""
    __tablename__ = "billing_history"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Transaction details
    transaction_type = Column(String(50), nullable=False)  # subscription, upgrade, credits, one_time
    transaction_id = Column(String(255), nullable=True, unique=True)  # Stripe payment ID
    
    # Amount
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    
    # Plan details
    plan_from = Column(String(20), nullable=True)
    plan_to = Column(String(20), nullable=True)
    
    # Credits
    credits_added = Column(Integer, default=0)
    credits_balance_after = Column(Integer, default=0)
    
    # Payment method
    payment_method = Column(String(50), nullable=True)  # card, paypal, etc.
    last_4_digits = Column(String(4), nullable=True)
    
    # Status
    status = Column(String(20), default="pending")  # pending, completed, failed, refunded
    
    # Stripe details
    stripe_invoice_id = Column(String(255), nullable=True)
    stripe_charge_id = Column(String(255), nullable=True)
    
    # Metadata (transaction metadata)
    transaction_metadata = Column(JSONB(), nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    completed_at = Column(TIMESTAMP, nullable=True)
    
    def __repr__(self):
        return f"<BillingHistory(user_id='{self.user_id}', type='{self.transaction_type}', status='{self.status}')>"


class Subscription(Base):
    """Active subscriptions"""
    __tablename__ = "subscriptions"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Subscription details
    plan = Column(String(20), nullable=False)  # free, plus, pro, ultra
    status = Column(String(20), default="active")  # active, canceled, past_due, paused
    
    # Billing
    billing_cycle = Column(String(20), default="monthly")  # monthly, yearly
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    
    # Stripe
    stripe_subscription_id = Column(String(255), nullable=True, unique=True)
    stripe_customer_id = Column(String(255), nullable=True)
    stripe_price_id = Column(String(255), nullable=True)
    
    # Dates
    current_period_start = Column(TIMESTAMP, nullable=True)
    current_period_end = Column(TIMESTAMP, nullable=True, index=True)
    trial_end = Column(TIMESTAMP, nullable=True)
    canceled_at = Column(TIMESTAMP, nullable=True)
    
    # Auto-renewal
    cancel_at_period_end = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Subscription(user_id='{self.user_id}', plan='{self.plan}', status='{self.status}')>"


class CreditsPurchase(Base):
    """Track one-time credit purchases"""
    __tablename__ = "credits_purchases"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Purchase details
    credits_amount = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    
    # Payment
    stripe_payment_intent_id = Column(String(255), nullable=True)
    status = Column(String(20), default="pending")  # pending, completed, failed
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    completed_at = Column(TIMESTAMP, nullable=True)
    
    def __repr__(self):
        return f"<CreditsPurchase(user_id='{self.user_id}', credits={self.credits_amount})>"
