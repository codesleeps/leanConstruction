#!/bin/bash

echo "🚀 Starting Lean Construction AI Backend (Simple Method)..."

cd /var/www/lean-construction

# Kill any existing processes
pkill -f "python.*minimal_backend" 2>/dev/null
pkill -f "uvicorn.*app.main" 2>/dev/null
sleep 2

# Start backend directly
echo "Starting FastAPI server..."
source venv/bin/activate
nohup python minimal_backend.py > backend.log 2>&1 &

# Get the PID
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Save PID for later management
echo $BACKEND_PID > backend.pid

# Wait a moment for startup
sleep 5

# Test the API
echo "Testing API endpoints..."
curl -s http://localhost:8000/ && echo -e "\n✅ API is responding!"

# Show logs if there were issues
if ! curl -s http://localhost:8000/ > /dev/null; then
    echo "❌ API not responding, checking logs:"
    tail -20 backend.log
fi

echo "Backend management commands:"
echo "  Stop: kill \$(cat backend.pid)"
echo "  Logs: tail -f backend.log"
echo "  Status: curl http://localhost:8000/"