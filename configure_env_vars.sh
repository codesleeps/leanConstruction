#!/bin/bash
# Sprint 1: Configure Environment Variables on VPS

echo "🔧 Configuring Environment Variables for Production..."

# Backend environment
cat > ~/apps/leanConstruction/backend/.env.production << 'EOF'
# Production Environment Configuration
ENVIRONMENT=production
API_URL=https://leanaiconstruction.com/api
FRONTEND_URL=https://leanaiconstruction.com

# Database Configuration  
DATABASE_URL=postgresql://user:password@localhost:5432/lean_construction

# Security
SECRET_KEY=jIkDfN_DV2M0Cz35A83N8-RQS8z5G98cZOHHvvKSnDw
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration (Production)
CORS_ALLOWED_ORIGINS=https://leanaiconstruction.com,https://www.leanaiconstruction.com
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOW_HEADERS=Authorization,Content-Type

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
EOF

echo "✅ Backend .env.production configured"

# Frontend environment
cat > ~/apps/leanConstruction/website/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=https://leanaiconstruction.com/api
EOF

echo "✅ Frontend .env.local configured"

# Restart services to apply changes
echo "🔄 Restarting services..."
sudo systemctl restart lean-backend
sudo systemctl restart lean-website

echo "✅ Services restarted"
echo "🎉 Environment configuration complete!"
