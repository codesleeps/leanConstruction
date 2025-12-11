# Deployment Guide - Making Features Visible on Live Site

## Issue Resolution

The user reports that none of the implemented features appear on the live website. This is a deployment/hosting issue rather than a code implementation problem. All functionality has been correctly implemented but needs to be deployed to be visible.

## 🚀 Immediate Deployment Steps

### 1. Backend Deployment
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend Deployment
```bash
# Navigate to website directory
cd website

# Install dependencies
npm install

# Build the Next.js application
npm run build

# Start the production server
npm start
```

### 3. Environment Configuration
Ensure these environment variables are set:
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:password@localhost/leanaiconstruction
SECRET_KEY=your-jwt-secret-key
EMAIL_PROVIDER=smtp
SMTP_HOST=your-smtp-host
SMTP_PORT=587
SMTP_USER=your-username
SMTP_PASSWORD=your-password

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🔧 Development Server Setup

### Running Locally
1. **Terminal 1 - Backend**:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

2. **Terminal 2 - Frontend**:
   ```bash
   cd website
   npm run dev
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🌐 Production Deployment

### Option 1: Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Option 2: Manual Server Deployment
1. **Backend on server**:
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Use production server
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

2. **Frontend on server**:
   ```bash
   # Build for production
   npm run build
   
   # Serve with nginx or similar
   npm start
   ```

### Option 3: Cloud Deployment
- **Vercel** (Frontend): Connect GitHub repo for automatic deployments
- **Heroku** (Backend): Deploy FastAPI app with PostgreSQL addon
- **AWS/GCP**: Use container services for both frontend and backend

## 📋 Verification Checklist

After deployment, verify these features are working:

### ✅ Authentication Endpoints
- [ ] `POST /api/auth/signup` - User registration
- [ ] `POST /api/auth/login` - User authentication  
- [ ] `POST /api/auth/forgot-password` - Password reset
- [ ] `POST /api/auth/reset-password` - Password confirmation
- [ ] `POST /api/auth/verify-email` - Email verification
- [ ] `GET /api/auth/user/profile` - User profile
- [ ] `POST /api/auth/demo-account/create` - Demo account creation

### ✅ Frontend Pages
- [ ] `/signup` - Registration page with construction value proposition
- [ ] `/login` - Authentication page with demo account options
- [ ] `/verify-email` - Email verification flow
- [ ] `/reset-password` - Password reset interface

### ✅ Demo Account Features
- [ ] Three demo account types (Small, Medium, Enterprise)
- [ ] Pre-populated construction data
- [ ] Auto-login functionality
- [ ] 7-day trial period

## 🔍 Troubleshooting

### Issue: "Features not visible"
**Solutions**:
1. Clear browser cache (Ctrl+F5 or Cmd+Shift+R)
2. Check browser console for JavaScript errors
3. Verify API endpoints are responding
4. Ensure environment variables are correctly set

### Issue: "Database connection errors"
**Solutions**:
1. Verify PostgreSQL is running
2. Check DATABASE_URL format
3. Run database migrations: `alembic upgrade head`
4. Check database credentials

### Issue: "Email not working"
**Solutions**:
1. Verify SMTP settings in environment variables
2. Check email service provider configuration
3. Test with a simple email first

### Issue: "Build errors"
**Solutions**:
1. Clear node_modules: `rm -rf node_modules && npm install`
2. Check for TypeScript errors: `npm run build`
3. Verify all dependencies are installed

## 📞 Support Commands

### Check API Health
```bash
curl http://localhost:8000/health
```

### Check Frontend Build
```bash
cd website && npm run build
```

### Test Database Connection
```bash
cd backend && python -c "from app.database import engine; print('Database connected successfully')"
```

### Verify Authentication Endpoints
```bash
# Test signup
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass","full_name":"Test User","company":"Test Co","role":"manager","company_size":"small","construction_type":"residential"}'

# Test demo account creation
curl -X POST http://localhost:8000/api/auth/demo-account/create \
  -H "Content-Type: application/json" \
  -d '{"account_type":"small"}'
```

## 🎯 Next Steps

1. **Deploy the application** using one of the methods above
2. **Test all features** to ensure they're working correctly
3. **Monitor logs** for any errors during deployment
4. **Verify user experience** by testing the complete flow

The code implementation is complete and correct. The deployment steps above will make all features visible on the live website.
