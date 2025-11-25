"""
Credits management utilities
Centralized logic for checking and deducting credits
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from backend.models.user import User
from backend.models.analytics import Analytics
from backend.config import settings
import uuid
from datetime import datetime


async def check_and_deduct_credits(
    user: User,
    cost: int,
    db: Session,
    operation: str = "general",
    metadata: dict = None
) -> bool:
    """
    Check if user has sufficient credits and deduct them
    
    Args:
        user: User object
        cost: Credit cost for operation
        db: Database session
        operation: Type of operation (for analytics)
        metadata: Additional metadata to log
    
    Returns:
        bool: True if credits deducted successfully
    
    Raises:
        HTTPException: If insufficient credits
    """
    # Check if user has enough credits
    if not user.has_credits(cost):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={
                "error": "insufficient_credits",
                "message": f"Insufficient credits. Required: {cost}, Available: {user.credits_remaining}",
                "required": cost,
                "available": user.credits_remaining,
                "plan": user.plan
            }
        )
    
    # Deduct credits
    success = user.deduct_credits(cost)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deduct credits"
        )
    
    # Log analytics event
    analytics_event = Analytics(
        id=uuid.uuid4(),
        user_id=user.id,
        event_type="credit_deduction",
        event_category=operation,
        credits_used=cost,
        event_metadata=metadata or {},
        created_at=datetime.utcnow()
    )
    db.add(analytics_event)
    
    # Commit changes
    db.commit()
    db.refresh(user)
    
    return True


def get_operation_cost(operation: str) -> int:
    """
    Get credit cost for a specific operation
    
    Args:
        operation: Operation name
    
    Returns:
        int: Credit cost
    """
    cost_mapping = {
        "generate_presentation": settings.COST_GENERATE_PRESENTATION,
        "rewrite_text": settings.COST_REWRITE_TEXT,
        "translate": settings.COST_TRANSLATE,
        "generate_image": settings.COST_GENERATE_IMAGE,
        "magic_design": settings.COST_MAGIC_DESIGN,
        "smart_resize": settings.COST_SMART_RESIZE,
        "ai_suggestions": settings.COST_AI_SUGGESTIONS,
    }
    
    return cost_mapping.get(operation, 5)  # Default to 5 credits


def check_export_permission(user: User) -> bool:
    """
    Check if user has permission to export
    
    Args:
        user: User object
    
    Returns:
        bool: True if user can export
    
    Raises:
        HTTPException: If user cannot export
    """
    if not user.can_export():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "export_not_allowed",
                "message": "Export feature requires Plus plan or higher",
                "current_plan": user.plan,
                "upgrade_required": True
            }
        )
    
    return True


def check_feature_access(user: User, feature: str) -> bool:
    """
    Check if user has access to a specific feature
    
    Args:
        user: User object
        feature: Feature name
    
    Returns:
        bool: True if user has access
    
    Raises:
        HTTPException: If user doesn't have access
    """
    if not user.has_feature(feature):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "feature_not_available",
                "message": f"Feature '{feature}' requires plan upgrade",
                "current_plan": user.plan,
                "feature": feature
            }
        )
    
    return True


def add_credits(user: User, amount: int, db: Session, reason: str = "purchase") -> User:
    """
    Add credits to user account
    
    Args:
        user: User object
        amount: Credits to add
        db: Database session
        reason: Reason for credit addition
    
    Returns:
        User: Updated user object
    """
    user.credits_remaining += amount
    
    # Log analytics event
    analytics_event = Analytics(
        id=uuid.uuid4(),
        user_id=user.id,
        event_type="credit_addition",
        event_category=reason,
        credits_used=-amount,  # Negative for addition
        event_metadata={"amount": amount, "reason": reason},
        created_at=datetime.utcnow()
    )
    db.add(analytics_event)
    db.commit()
    db.refresh(user)
    
    return user


def reset_monthly_credits(user: User, db: Session) -> User:
    """
    Reset monthly credits for paid plans
    
    Args:
        user: User object
        db: Database session
    
    Returns:
        User: Updated user object
    """
    from backend.config import PLAN_CONFIGS
    
    plan_config = PLAN_CONFIGS.get(user.plan)
    if plan_config and plan_config.get('monthly_credits', 0) > 0:
        user.credits_remaining = plan_config['monthly_credits']
        user.credits_reset_date = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
    
    return user
