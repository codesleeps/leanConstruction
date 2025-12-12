from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import stripe
from ..auth import get_current_active_user
from ..models import User

router = APIRouter(prefix="/api/payments", tags=["payments"])

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Mock subscription data (fallback)
mock_subscriptions = {}

class CreateSubscriptionRequest(BaseModel):
    price_id: str
    customer_id: Optional[str] = None

class ConfirmSubscriptionRequest(BaseModel):
    payment_method_id: str
    customer_id: str
    client_secret: str # Not strictly needed for logic but might be passed back

class CancelSubscriptionRequest(BaseModel):
    subscription_id: str

@router.post("/create-subscription")
async def create_subscription(
    request: CreateSubscriptionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Create a subscription intent (Real Stripe or Mock)"""
    
    # Use real Stripe if configured
    if stripe.api_key:
        try:
            # 1. Get or create customer
            # In a real app, you'd store stripe_customer_id on the User model
            # identifying by email for simplicity here
            customers = stripe.Customer.list(email=current_user.email, limit=1)
            if customers.data:
                customer_id = customers.data[0].id
            else:
                customer = stripe.Customer.create(
                    email=current_user.email,
                    name=current_user.full_name
                )
                customer_id = customer.id
            
            # 2. Create subscription
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': request.price_id}],
                payment_behavior='default_incomplete',
                payment_settings={'save_default_payment_method': 'on_subscription'},
                expand=['latest_invoice.payment_intent'],
            )
            
            return {
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "subscription_id": subscription.id,
                "status": "requires_payment_method"
            }
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
            
    # Mock Fallback
    else:
        try:
            # Mock response
            client_secret = f"pi_mock_{request.price_id}_{hash(request.customer_id or 'demo')}secret"
            
            return {
                "client_secret": client_secret,
                "subscription_id": f"sub_mock_{request.price_id}",
                "status": "requires_payment_method",
                "mode": "test_mock"
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

@router.post("/confirm-subscription")
async def confirm_subscription(request: ConfirmSubscriptionRequest):
    """Confirm subscription payment (Mock only, Stripe handles this via webhooks or client-side confirm)"""
    
    # If using real Stripe, the client-side confirmCardPayment handles the confirmation.
    # The server side usually just listens for webhooks.
    # But for a hybrid endpoint, we can return success.
    
    if stripe.api_key:
        return {
            "success": True,
            "message": "Payment should be confirmed on client side. Webhook will update status."
        }

    try:
        # Mock successful payment confirmation
        subscription_id = f"sub_mock_{hash(request.customer_id)}"
        
        mock_subscriptions[request.customer_id] = {
            "id": subscription_id,
            "status": "active",
            "plan": {
                "id": "professional",
                "name": "Professional",
                "price": 79
            },
            "current_period_end": "2025-01-09",
            "customer_id": request.customer_id
        }
        
        return {
            "success": True,
            "subscription": mock_subscriptions[request.customer_id],
            "message": "Subscription created successfully!"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/subscription-status")
async def get_subscription_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get current subscription status for the user"""
    
    if stripe.api_key:
        try:
            customers = stripe.Customer.list(email=current_user.email, limit=1)
            if not customers.data:
                 return {"status": "inactive"}
            
            customer_id = customers.data[0].id
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                status='active',
                limit=1
            )
            
            if subscriptions.data:
                sub = subscriptions.data[0]
                return {
                    "id": sub.id,
                    "status": sub.status,
                    "plan": {
                        "id": sub.plan.id,
                        "interval": sub.plan.interval,
                        "amount": sub.plan.amount
                    },
                    "current_period_end": sub.current_period_end # timestamp
                }
            return {"status": "inactive"}
            
        except Exception as e:
             raise HTTPException(status_code=500, detail=str(e))
             
    # Mock Fallback
    try:
        # For demo purposes, we can assume the user has a mock customer_id related to their ID
        customer_id = str(current_user.id) 
        subscription = mock_subscriptions.get(customer_id)
        if subscription:
            return subscription
        else:
            return {
                "id": None,
                "status": "inactive",
                "plan": None,
                "current_period_end": None,
                "customer_id": customer_id
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cancel-subscription")
async def cancel_subscription(
    request: CancelSubscriptionRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Cancel a subscription"""
    
    if stripe.api_key:
        try:
            stripe.Subscription.delete(request.subscription_id)
            return {
                "success": True,
                "message": "Subscription cancelled successfully"
            }
        except Exception as e:
             return {"success": False, "error": str(e)}

    # Mock Fallback
    try:
        for customer_id, sub in list(mock_subscriptions.items()):
            if sub["id"] == request.subscription_id:
                del mock_subscriptions[customer_id]
                return {
                    "success": True,
                    "message": "Subscription cancelled successfully"
                }
        
        return {
            "success": False,
            "error": "Subscription not found"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }