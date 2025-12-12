#!/bin/bash

# VPS Deployment Recovery Script
# Handles SSH connection issues and attempts automated deployment

VPS_HOST="srv1187860.hstgr.cloud"
VPS_IP="72.61.16.111"
DEPLOYMENT_SCRIPTS=(
    "production-deployment-orchestrator.sh"
    "fix-deployment-issues.sh"
    "deploy-frontend.sh"
    "check-deployment-status.sh"
    "vps-current-state-analysis.sh"
)

echo "🚀 VPS Deployment Recovery Script"
echo "================================="
echo "Target: $VPS_HOST ($VPS_IP)"

# Function to try SSH connection
try_ssh_connection() {
    local user=$1
    local key=$2
    
    echo "Trying SSH: $user@$VPS_HOST with key $key"
    
    # Test connection with simple command
    if ssh -o ConnectTimeout=10 -o BatchMode=yes -i "$key" "$user@$VPS_HOST" "echo 'SSH_SUCCESS' && pwd" 2>/dev/null | grep -q "SSH_SUCCESS"; then
        echo "✅ SSH connection successful with $user@$VPS_HOST"
        return 0
    else
        echo "❌ SSH connection failed with $user@$VPS_HOST"
        return 1
    fi
}

# Function to upload scripts
upload_scripts() {
    local user=$1
    local key=$2
    
    echo "Uploading deployment scripts..."
    
    for script in "${DEPLOYMENT_SCRIPTS[@]}"; do
        if [ -f "$script" ]; then
            echo "Uploading $script..."
            scp -o ConnectTimeout=10 -o StrictHostKeyChecking=no -i "$key" "$script" "$user@$VPS_HOST:~/" 2>/dev/null && echo "✅ $script uploaded" || echo "❌ $script upload failed"
        else
            echo "⚠️  $script not found, skipping"
        fi
    done
}

# Function to execute deployment
execute_deployment() {
    local user=$1
    local key=$2
    
    echo "Executing deployment..."
    
    # Make scripts executable
    ssh -o ConnectTimeout=10 -i "$key" "$user@$VPS_HOST" "chmod +x *.sh" 2>/dev/null
    
    # Run the orchestrator
    ssh -o ConnectTimeout=10 -i "$key" "$user@$VPS_HOST" "./production-deployment-orchestrator.sh" 2>/dev/null
}

# Main execution
echo "Attempting SSH connections..."

# Try different user/key combinations
USERS=("root" "ubuntu" "admin" "deploy")
KEYS=("~/.ssh/vps_deploy_key" "~/.ssh/id_ed25519")

for user in "${USERS[@]}"; do
    for key in "${KEYS[@]}"; do
        if try_ssh_connection "$user" "$key"; then
            echo "🎉 SSH access established!"
            echo "Uploading scripts..."
            upload_scripts "$user" "$key"
            echo "Executing deployment..."
            execute_deployment "$user" "$key"
            echo "Deployment process initiated!"
            exit 0
        fi
    done
done

echo "❌ All SSH connection attempts failed"
echo "Manual intervention required"
exit 1
