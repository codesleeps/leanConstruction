#!/bin/bash
# Enable Ubuntu Pro ESM (Expanded Security Maintenance)

echo "🔒 Enabling Ubuntu Pro ESM..."
echo ""

# Check if already enabled
if sudo pro status | grep -q "esm-apps.*enabled"; then
    echo "✅ ESM Apps is already enabled!"
    exit 0
fi

# Enable ESM Apps (free for up to 5 machines for personal use)
echo "📝 To enable ESM, you have two options:"
echo ""
echo "Option 1: Enable ESM Apps (Free for personal use, up to 5 machines)"
echo "   sudo pro enable esm-apps"
echo ""
echo "Option 2: Attach to Ubuntu Pro (requires free account)"
echo "   1. Get a token from: https://ubuntu.com/pro"
echo "   2. Run: sudo pro attach <your-token>"
echo ""

# Attempt automatic enablement
echo "Attempting to enable ESM Apps..."
sudo pro enable esm-apps --assume-yes

if [ $? -eq 0 ]; then
    echo "✅ ESM Apps enabled successfully!"
else
    echo "⚠️  Could not auto-enable. You may need an Ubuntu Pro token."
    echo "   Visit: https://ubuntu.com/pro to get a free token"
    echo "   Then run: sudo pro attach <your-token>"
fi

echo ""
echo "Current status:"
sudo pro status
