# Payment-Only Server

This directory contains a lightweight payment-only server that doesn't require heavy ML dependencies like PyTorch, OpenCV, or scikit-learn.

## 🚀 Quick Start

### Option 1: Using the Startup Script (Recommended)

```bash
cd backend
./start-payment-server.sh
```

### Option 2: Manual Startup

```bash
cd backend
pip install -r requirements-minimal.txt
cd app
python payments_only.py
```

The server will start on `http://localhost:8000`

## 📖 API Documentation

Once the server is running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc

## 💳 Payment Endpoints

The payment-only server provides these endpoints:

### Create Subscription
```http
POST /api/v1/payments/create-subscription
Content-Type: application/json

{
    "price_id": "price_1234567890",
    "customer_id": "cus_1234567890"
}
```

### Confirm Subscription
```http
POST /api/v1/payments/confirm-subscription
Content-Type: application/json

{
    "payment_method_id": "pm_1234567890",
    "customer_id": "cus_1234567890",
    "client_secret": "pi_1234567890_secret_..."
}
```

### Get Subscription Status
```http
GET /api/v1/payments/subscription-status/{customer_id}
```

### Cancel Subscription
```http
POST /api/v1/payments/cancel-subscription
Content-Type: application/json
## 🏭 Production Deployment

For production environments, use the enhanced production server:

### Production Server Features
- **Database Persistence**: PostgreSQL/MySQL with connection pooling
- **Real Stripe Integration**: Live payment processing with webhooks
- **Redis Caching**: High-performance caching layer
- **Security**: Enterprise-grade authentication and rate limiting
- **Monitoring**: Health checks, metrics, and structured logging
- **Scalability**: Horizontal scaling and load balancer ready

### Production Setup
```bash
cd backend
pip install -r requirements-production.txt
cd app
python payments_production.py
```

**Environment Variables Required:**
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/payments
REDIS_URL=redis://localhost:6379/0
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=https://yourdomain.com
```

See `PRODUCTION_DEPLOYMENT_GUIDE.md` for complete deployment instructions.



{
    "subscription_id": "sub_1234567890"
}
```

## 🔍 Health Check

Check server status:
```http
GET /health
```

## 🆚 Comparison with Full Server

| Feature | Payment-Only Server | Full Server (main.py) |
|---------|-------------------|---------------------|
| **Dependencies** | Minimal (8 packages) | Heavy (22+ packages) |
| **ML Modules** | ❌ None | ✅ All ML features |
| **Payment Processing** | ✅ Full support | ✅ Full support |
| **Computer Vision** | ❌ Not available | ✅ Available |
| **Waste Detection** | ❌ Not available | ✅ Available |
| **Forecasting** | ❌ Not available | ✅ Available |
| **Database** | ❌ In-memory only | ✅ Full database |
| **Authentication** | ❌ Basic only | ✅ Full auth system |
| **Startup Time** | ~2 seconds | ~15-30 seconds |
| **Memory Usage** | ~50MB | ~500MB+ |

## 🛠️ Development

### Testing Payment Endpoints

Use the included mock data for testing:

```bash
# Test subscription creation
curl -X POST "http://localhost:8000/api/v1/payments/create-subscription" \
     -H "Content-Type: application/json" \
     -d '{"price_id": "price_test", "customer_id": "cus_test"}'

# Test subscription status
curl "http://localhost:8000/api/v1/payments/subscription-status/cus_test"
```

### Dependencies

The payment-only server uses only these packages:

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `python-multipart` - Form data parsing
- `python-jose` - JWT token handling
- `passlib` - Password hashing
- `python-decouple` - Environment variables
- `httpx` - HTTP client
- `requests` - HTTP library

**Total size**: ~50MB vs ~2GB+ for the full server with ML dependencies.

## 🚨 Important Notes

1. **Mock Implementation**: This server uses mock payment data for demonstration. In production, integrate with a real payment processor like Stripe.

2. **No Database**: The payment-only server stores data in memory only. For persistence, use the full server or add database integration.

3. **No Authentication**: This simplified version doesn't include the full authentication system. Add authentication middleware as needed.

4. **ML Features**: If you need ML features (computer vision, waste detection, forecasting, etc.), use the full server with `main.py`.

## 📁 File Structure

```
backend/
├── app/
│   ├── payments_only.py      # Main payment server file
│   └── api/
│       └── payments.py       # Payment route definitions
├── requirements-minimal.txt  # Minimal dependencies
├── start-payment-server.sh  # Startup script
└── PAYMENT_SERVER_README.md # This file
```

## 🔧 Troubleshooting

### Port Already in Use
If port 8000 is already in use, modify the port in `app/payments_only.py`:

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Change to 8001
```

### Import Errors
Ensure you're running from the correct directory and all dependencies are installed:

```bash
cd backend
pip install -r requirements-minimal.txt
```

### Testing Connection
Check if the server is running:

```bash
curl http://localhost:8000/health
```

Should return:
```json
{
    "status": "healthy",
    "timestamp": "2025-12-09T17:25:31.791Z",
    "version": "1.0.0",
    "modules": {
        "payments": "available"
    }
}
```

## 🎯 Use Cases

Use the payment-only server when you need:

- ✅ Quick payment testing and integration
- ✅ Frontend development without ML dependencies
- ✅ CI/CD pipelines with minimal setup time
- ✅ Development environments with limited resources
- ✅ Demonstrating payment functionality separately from ML features

Use the full server when you need:

- ✅ Full ML capabilities (computer vision, waste detection, etc.)
- ✅ Database persistence
- ✅ Complete authentication system
- ✅ Production deployment with all features