# Deployment Status - leanaiconstruction.com

## ✅ Working
- Website deployed: https://leanaiconstruction.com
- SSL certificate active
- Frontend (React dashboard) built
- Next.js website running
- Nginx configured
- Backend service running (without ML features)

## ❌ Not Working
- Chatbot (backend chat endpoints disabled)
- ML features (PyTorch not installed)
- Dashboard functionality

## 🔧 To Fix Everything

### Option 1: Install ML Dependencies (Complete App)
```bash
ssh root@srv1187860.hstgr.cloud
cd /var/www/lean-ai-construction/backend

# Install ML packages (~2GB, takes 5-10 min)
./venv/bin/pip install torch torchvision transformers pillow opencv-python-headless scikit-learn numpy pandas

# Uncomment ML routes
sed -i 's/^# from .api.ml_routes/from .api.ml_routes/g' app/main.py
sed -i 's/^#     app.include_router(ml_router/    app.include_router(ml_router/g' app/main.py

# Restart
systemctl restart lean-backend
systemctl status lean-backend
```

### Option 2: Quick Basic Backend (No ML)
The backend is already running with basic API routes. To verify what's available:
```bash
curl https://leanaiconstruction.com/docs
```

## 📝 Environment Variables Needed

Backend needs `.env` file at `/var/www/lean-ai-construction/backend/.env`:
```env
DATABASE_URL=postgresql://user:pass@localhost/dbname
SECRET_KEY=your-secret-key-here
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
```

Create it:
```bash
nano /var/www/lean-ai-construction/backend/.env
# Add variables above, then Ctrl+X, Y, Enter
systemctl restart lean-backend
```

## 🔍 Debugging Commands

```bash
# Check backend logs
journalctl -u lean-backend -n 50 --no-pager

# Check website logs  
journalctl -u lean-website -n 50 --no-pager

# Check nginx logs
tail -f /var/log/nginx/error.log

# Restart all services
systemctl restart lean-backend lean-website nginx
```

## 📂 Files Modified

Local:
- `/Users/test/Desktop/leanConstruction/website/src/components/ui/ChatWidget.tsx`
- `/Users/test/Desktop/leanConstruction/deploy_unified.sh`

VPS:
- `/var/www/lean-ai-construction/backend/app/main.py` (ML routes commented out)
- `/var/www/lean-ai-construction/backend/venv/` (Python packages installed)

## 🎯 Next Steps Priority

1. **For working app**: Run Option 1 commands (install ML deps)
2. **For basic site**: Add environment variables
3. **For testing**: Check `/docs` endpoint to see available APIs
