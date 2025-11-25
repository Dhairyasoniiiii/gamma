"""
Billing API Endpoints
Handles subscriptions, payments, and invoicing
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from backend.db.base import get_db
from backend.models.user import User
from backend.utils.auth import get_current_user
from backend.services.billing_service import billing_service
from backend.config import PLAN_CONFIGS

router = APIRouter(prefix="/api/v1/billing", tags=["Billing"])


# Pydantic Schemas
class SubscribeRequest(BaseModel):
    plan: str  # plus, pro, ultra
    billing_period: str = "monthly"  # monthly, yearly
    payment_method_id: Optional[str] = None


class PaymentMethodRequest(BaseModel):
    payment_method_id: str


# Get Available Plans
@router.get("/plans")
async def get_plans():
    """
    Get all available subscription plans
    """
    return {
        "plans": [
            {
                "id": "free",
                "name": "Free",
                "price": {"monthly": 0, "yearly": 0},
                "features": PLAN_CONFIGS["free"]
            },
            {
                "id": "plus",
                "name": "Plus",
                "price": {"monthly": 8, "yearly": 80},
                "features": PLAN_CONFIGS["plus"]
            },
            {
                "id": "pro",
                "name": "Pro",
                "price": {"monthly": 15, "yearly": 150},
                "features": PLAN_CONFIGS["pro"]
            },
            {
                "id": "ultra",
                "name": "Ultra",
                "price": {"monthly": 25, "yearly": 250},
                "features": PLAN_CONFIGS["ultra"]
            }
        ]
    }


# Subscribe to Plan
@router.post("/subscribe")
async def subscribe(
    data: SubscribeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Subscribe to a paid plan
    """
    # Validate plan
    if data.plan not in ["plus", "pro", "ultra"]:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    # Check if user already has a subscription
    if current_user.stripe_subscription_id:
        raise HTTPException(
            status_code=400,
            detail="Already subscribed. Use upgrade/downgrade endpoint."
        )
    
    try:
        # Create Stripe customer if doesn't exist
        if not current_user.stripe_customer_id:
            customer = billing_service.create_customer(
                user_id=current_user.id,
                email=current_user.email,
                name=current_user.full_name
            )
            current_user.stripe_customer_id = customer["id"]
            db.commit()
        
        # Add payment method if provided
        if data.payment_method_id:
            billing_service.add_payment_method(
                current_user.stripe_customer_id,
                data.payment_method_id
            )
        
        # Create subscription
        subscription = billing_service.create_subscription(
            stripe_customer_id=current_user.stripe_customer_id,
            plan=data.plan,
            billing_period=data.billing_period
        )
        
        # Update user
        current_user.plan = data.plan
        current_user.stripe_subscription_id = subscription["id"]
        
        # Update credits based on plan
        current_user.credits = PLAN_CONFIGS[data.plan]["credits_per_month"]
        
        db.commit()
        
        return {
            "status": "subscribed",
            "plan": data.plan,
            "subscription_id": subscription["id"],
            "credits": current_user.credits
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Upgrade/Downgrade Plan
@router.post("/change-plan")
async def change_plan(
    data: SubscribeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upgrade or downgrade current plan
    """
    if not current_user.stripe_subscription_id:
        raise HTTPException(
            status_code=400,
            detail="No active subscription. Use subscribe endpoint."
        )
    
    # Validate plan
    if data.plan not in ["plus", "pro", "ultra"]:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    # Can't downgrade to current plan
    if data.plan == current_user.plan:
        raise HTTPException(
            status_code=400,
            detail="Already on this plan"
        )
    
    try:
        # Update subscription
        subscription = billing_service.update_subscription(
            current_user.stripe_subscription_id,
            data.plan
        )
        
        # Update user
        current_user.plan = data.plan
        current_user.credits = PLAN_CONFIGS[data.plan]["credits_per_month"]
        
        db.commit()
        
        return {
            "status": "updated",
            "plan": data.plan,
            "credits": current_user.credits
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Cancel Subscription
@router.post("/cancel")
async def cancel_subscription(
    immediate: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel subscription
    
    - **immediate**: Cancel immediately (True) or at period end (False)
    """
    if not current_user.stripe_subscription_id:
        raise HTTPException(status_code=400, detail="No active subscription")
    
    try:
        result = billing_service.cancel_subscription(
            current_user.stripe_subscription_id,
            immediate=immediate
        )
        
        if immediate:
            # Downgrade to free plan immediately
            current_user.plan = "free"
            current_user.credits = PLAN_CONFIGS["free"]["credits_per_month"]
            current_user.stripe_subscription_id = None
            db.commit()
        
        return {
            "status": "canceled" if immediate else "will_cancel",
            "message": "Subscription canceled immediately" if immediate else "Subscription will cancel at period end"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Add Payment Method
@router.post("/payment-methods")
async def add_payment_method(
    data: PaymentMethodRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a payment method
    """
    if not current_user.stripe_customer_id:
        # Create customer first
        customer = billing_service.create_customer(
            user_id=current_user.id,
            email=current_user.email,
            name=current_user.full_name
        )
        current_user.stripe_customer_id = customer["id"]
        db.commit()
    
    try:
        result = billing_service.add_payment_method(
            current_user.stripe_customer_id,
            data.payment_method_id
        )
        return {"status": "added", "payment_method_id": result["id"]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get Payment Methods
@router.get("/payment-methods")
async def get_payment_methods(
    current_user: User = Depends(get_current_user)
):
    """
    Get all payment methods
    """
    if not current_user.stripe_customer_id:
        return {"payment_methods": []}
    
    try:
        methods = billing_service.get_payment_methods(
            current_user.stripe_customer_id
        )
        return {"payment_methods": methods}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get Invoices
@router.get("/invoices")
async def get_invoices(
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """
    Get billing invoices
    """
    if not current_user.stripe_customer_id:
        return {"invoices": []}
    
    try:
        invoices = billing_service.get_invoices(
            current_user.stripe_customer_id,
            limit=limit
        )
        return {"invoices": invoices}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Get Current Subscription
@router.get("/subscription")
async def get_subscription(
    current_user: User = Depends(get_current_user)
):
    """
    Get current subscription details
    """
    return {
        "plan": current_user.plan,
        "credits": current_user.credits,
        "subscription_id": current_user.stripe_subscription_id,
        "features": PLAN_CONFIGS[current_user.plan]
    }


# Stripe Webhook
@router.post("/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events
    """
    try:
        payload = await request.body()
        signature = request.headers.get("stripe-signature")
        
        result = billing_service.handle_webhook(payload, signature)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Get Billing Portal
@router.get("/portal")
async def get_billing_portal(
    current_user: User = Depends(get_current_user)
):
    """
    Get Stripe billing portal link
    """
    if not current_user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No billing account")
    
    # In production: Create Stripe billing portal session
    return {
        "url": f"https://billing.stripe.com/p/login/test_{current_user.stripe_customer_id}"
    }
