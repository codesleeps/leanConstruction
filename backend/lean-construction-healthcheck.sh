#!/bin/bash

API_URL="http://localhost:8000/health"

if ! curl -f -s "$API_URL" > /dev/null; then
    echo "[$(date)] Backend health check failed, restarting..." >> /var/log/lean-construction-health.log
    pm2 restart lean-construction-api
    sleep 10
    if ! curl -f -s "$API_URL" > /dev/null; then
        echo "[$(date)] Restart failed, trying systemd..." >> /var/log/lean-construction-health.log
        sudo systemctl restart lean-construction-backend
    fi
fi