from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

# Mock subscription data
mock_subscriptions = {}

class CreateSubscriptionRequest(BaseModel):
    price_id: str
    customer_id: Optional[str] = None

class ConfirmSubscriptionRequest(BaseModel):
    payment_method_id: str
    customer_id: str
    client_secret: str

class CancelSubscriptionRequest(BaseModel):
    subscription_id: str

@router.post("/create-subscription")
async def create_subscription(request: CreateSubscriptionRequest):
    """Mock endpoint to create a subscription intent"""
    try:
        # Mock response - in production this would call Stripe
        client_secret = f"pi_mock_{request.price_id}_{hash(request.customer_id or 'demo')}secret"
        
        return {
            "client_secret": client_secret,
            "subscription_id": f"sub_mock_{request.price_id}",
            "status": "requires_payment_method"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/confirm-subscription")
async def confirm_subscription(request: ConfirmSubscriptionRequest):
    """Mock endpoint to confirm subscription payment"""
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

@router.get("/subscription-status/{customer_id}")
async def get_subscription_status(customer_id: str):
    """Get current subscription status for a customer"""
    try:
        subscription = mock_subscriptions.get(customer_id)
        if subscription:
            return subscription
        else:
            # Return no active subscription
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
async def cancel_subscription(request: CancelSubscriptionRequest):
    """Cancel a subscription"""
    try:
        # Find and remove subscription
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