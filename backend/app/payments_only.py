"""
Simple payment-only API server for testing Stripe integration
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Lean Construction AI - Payments API",
    description="Payment processing API for Stripe integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

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

@app.get("/")
async def root():
    return {
        "name": "Lean Construction AI - Payments API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "modules": {
            "payments": "available"
        }
    }

@app.post("/api/v1/payments/create-subscription")
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

@app.post("/api/v1/payments/confirm-subscription")
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

@app.get("/api/v1/payments/subscription-status/{customer_id}")
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

@app.post("/api/v1/payments/cancel-subscription")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)