#!/bin/bash

echo "🔧 Fixing backend deployment directory structure..."

# Create proper app directory structure
cd /var/www/lean-construction
mkdir -p app

# Extract from the original backend package to app directory
echo "Extracting backend files to app directory..."
cd /tmp
tar -xzf lean-construction-backend.tar.gz --strip-components=1 -C /var/www/lean-construction/app/

# Copy requirements.txt to root if it exists in app
if [ -f /var/www/lean-construction/app/requirements.txt ]; then
    cp /var/www/lean-construction/app/requirements.txt /var/www/lean-construction/
fi

# Set proper permissions
chown -R root:root /var/www/lean-construction
chmod -R 755 /var/www/lean-construction

# Create requirements.txt if missing
cd /var/www/lean-construction
if [ ! -f requirements.txt ]; then
    cat > requirements.txt << 'EOF'
fastapi==0.124.0
uvicorn[standard]==0.38.0
python-multipart==0.0.20
python-jose[cryptography]==3.5.0
python-dotenv==1.2.1
bcrypt==5.0.0
passlib==1.7.4
numpy>=1.21.0
pandas>=1.3.0
scikit-learn>=1.0.0
matplotlib>=3.3.0
seaborn>=0.11.0
plotly>=5.0.0
opencv-python>=4.5.0
pillow>=8.0.0
python-dateutil>=2.8.0
pytz>=2021.1
EOF
    echo "✅ Created requirements.txt"
fi

# Test the backend import
echo "Testing backend import..."
cd /var/www/lean-construction
source venv/bin/activate
python -c 'from app.main import app; print("✅ Backend imports successfully!")' 2>/dev/null && echo "✅ Import test passed!" || echo "❌ Import test failed"

# Show directory structure
echo "Directory structure:"
ls -la /var/www/lean-construction/
echo "App directory:"
ls -la /var/www/lean-construction/app/

echo "Fix completed!"