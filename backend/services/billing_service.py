"""
Billing Service
Handles Stripe integration, subscriptions, and payment processing
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
import os

# Stripe integration (optional - install with: pip install stripe)
try:
    import stripe
    stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False


class BillingService:
    """Service for handling billing and subscriptions"""
    
    def __init__(self):
        self.stripe_available = STRIPE_AVAILABLE
        
        # Plan pricing (in cents)
        self.plan_prices = {
            "plus": {
                "monthly": 800,  # $8/month
                "yearly": 8000   # $80/year (2 months free)
            },
            "pro": {
                "monthly": 1500,  # $15/month
                "yearly": 15000   # $150/year
            },
            "ultra": {
                "monthly": 2500,  # $25/month
                "yearly": 25000   # $250/year
            }
        }
    
    # ========== Customer Management ==========
    
    def create_customer(self, user_id: int, email: str, name: Optional[str] = None) -> dict:
        """
        Create a Stripe customer
        """
        if not self.stripe_available:
            return {"id": f"cus_mock_{user_id}", "email": email}
        
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={"user_id": user_id}
            )
            return {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name
            }
        except Exception as e:
            raise Exception(f"Failed to create customer: {str(e)}")
    
    def get_customer(self, stripe_customer_id: str) -> dict:
        """
        Get customer details from Stripe
        """
        if not self.stripe_available:
            return {"id": stripe_customer_id}
        
        try:
            customer = stripe.Customer.retrieve(stripe_customer_id)
            return {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name
            }
        except Exception as e:
            raise Exception(f"Failed to retrieve customer: {str(e)}")
    
    # ========== Subscription Management ==========
    
    def create_subscription(
        self,
        stripe_customer_id: str,
        plan: str,
        billing_period: str = "monthly"
    ) -> dict:
        """
        Create a subscription for a customer
        
        Args:
            stripe_customer_id: Stripe customer ID
            plan: Plan name (plus, pro, ultra)
            billing_period: monthly or yearly
        """
        if not self.stripe_available:
            return {
                "id": f"sub_mock_{stripe_customer_id}",
                "plan": plan,
                "status": "active",
                "current_period_end": (datetime.utcnow() + timedelta(days=30)).isoformat()
            }
        
        # In production: Create actual Stripe subscription
        try:
            # Get price ID from Stripe
            price_id = self._get_price_id(plan, billing_period)
            
            subscription = stripe.Subscription.create(
                customer=stripe_customer_id,
                items=[{"price": price_id}],
                metadata={"plan": plan, "billing_period": billing_period}
            )
            
            return {
                "id": subscription.id,
                "plan": plan,
                "status": subscription.status,
                "current_period_end": datetime.fromtimestamp(
                    subscription.current_period_end
                ).isoformat()
            }
        except Exception as e:
            raise Exception(f"Failed to create subscription: {str(e)}")
    
    def _get_price_id(self, plan: str, billing_period: str) -> str:
        """
        Get Stripe price ID for a plan
        (In production: Store these in database or environment variables)
        """
        price_ids = {
            "plus": {
                "monthly": "price_plus_monthly",
                "yearly": "price_plus_yearly"
            },
            "pro": {
                "monthly": "price_pro_monthly",
                "yearly": "price_pro_yearly"
            },
            "ultra": {
                "monthly": "price_ultra_monthly",
                "yearly": "price_ultra_yearly"
            }
        }
        return price_ids.get(plan, {}).get(billing_period, "")
    
    def cancel_subscription(self, subscription_id: str, immediate: bool = False) -> dict:
        """
        Cancel a subscription
        
        Args:
            subscription_id: Stripe subscription ID
            immediate: Cancel immediately (True) or at period end (False)
        """
        if not self.stripe_available:
            return {"id": subscription_id, "status": "canceled"}
        
        try:
            if immediate:
                subscription = stripe.Subscription.delete(subscription_id)
            else:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            
            return {
                "id": subscription.id,
                "status": subscription.status,
                "cancel_at_period_end": subscription.cancel_at_period_end
            }
        except Exception as e:
            raise Exception(f"Failed to cancel subscription: {str(e)}")
    
    def update_subscription(self, subscription_id: str, new_plan: str) -> dict:
        """
        Update (upgrade/downgrade) a subscription
        """
        if not self.stripe_available:
            return {"id": subscription_id, "plan": new_plan}
        
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Get new price ID
            new_price_id = self._get_price_id(new_plan, "monthly")
            
            # Update subscription
            updated = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription["items"]["data"][0].id,
                    "price": new_price_id
                }],
                proration_behavior="always_invoice"
            )
            
            return {
                "id": updated.id,
                "plan": new_plan,
                "status": updated.status
            }
        except Exception as e:
            raise Exception(f"Failed to update subscription: {str(e)}")
    
    # ========== Payment Methods ==========
    
    def add_payment_method(
        self,
        stripe_customer_id: str,
        payment_method_id: str
    ) -> dict:
        """
        Attach a payment method to a customer
        """
        if not self.stripe_available:
            return {"id": payment_method_id}
        
        try:
            # Attach payment method
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=stripe_customer_id
            )
            
            # Set as default
            stripe.Customer.modify(
                stripe_customer_id,
                invoice_settings={"default_payment_method": payment_method_id}
            )
            
            return {"id": payment_method_id, "status": "attached"}
        except Exception as e:
            raise Exception(f"Failed to add payment method: {str(e)}")
    
    def get_payment_methods(self, stripe_customer_id: str) -> list:
        """
        Get all payment methods for a customer
        """
        if not self.stripe_available:
            return []
        
        try:
            methods = stripe.PaymentMethod.list(
                customer=stripe_customer_id,
                type="card"
            )
            return [
                {
                    "id": pm.id,
                    "type": pm.type,
                    "card": {
                        "brand": pm.card.brand,
                        "last4": pm.card.last4,
                        "exp_month": pm.card.exp_month,
                        "exp_year": pm.card.exp_year
                    }
                }
                for pm in methods.data
            ]
        except Exception as e:
            raise Exception(f"Failed to get payment methods: {str(e)}")
    
    # ========== Invoicing ==========
    
    def get_invoices(self, stripe_customer_id: str, limit: int = 10) -> list:
        """
        Get invoices for a customer
        """
        if not self.stripe_available:
            return []
        
        try:
            invoices = stripe.Invoice.list(
                customer=stripe_customer_id,
                limit=limit
            )
            return [
                {
                    "id": inv.id,
                    "amount": inv.amount_paid / 100,  # Convert cents to dollars
                    "currency": inv.currency,
                    "status": inv.status,
                    "date": datetime.fromtimestamp(inv.created).isoformat(),
                    "pdf_url": inv.invoice_pdf
                }
                for inv in invoices.data
            ]
        except Exception as e:
            raise Exception(f"Failed to get invoices: {str(e)}")
    
    # ========== Webhooks ==========
    
    def handle_webhook(self, payload: dict, signature: str) -> dict:
        """
        Handle Stripe webhook events
        
        Events to handle:
        - customer.subscription.updated
        - customer.subscription.deleted
        - invoice.payment_succeeded
        - invoice.payment_failed
        """
        if not self.stripe_available:
            return {"status": "skipped"}
        
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            
            event_type = event["type"]
            data = event["data"]["object"]
            
            if event_type == "customer.subscription.updated":
                # Handle subscription update
                return {"status": "subscription_updated", "subscription_id": data["id"]}
            
            elif event_type == "customer.subscription.deleted":
                # Handle subscription cancellation
                return {"status": "subscription_deleted", "subscription_id": data["id"]}
            
            elif event_type == "invoice.payment_succeeded":
                # Handle successful payment
                return {"status": "payment_succeeded", "invoice_id": data["id"]}
            
            elif event_type == "invoice.payment_failed":
                # Handle failed payment
                return {"status": "payment_failed", "invoice_id": data["id"]}
            
            return {"status": "unhandled", "event_type": event_type}
        
        except Exception as e:
            raise Exception(f"Webhook error: {str(e)}")


# Singleton instance
billing_service = BillingService()
