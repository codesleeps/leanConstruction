#!/bin/bash

# ============================================
# Enhanced Monitoring Setup Script
# ============================================

echo "🔍 Setting up Enhanced Monitoring for Lean Construction AI"
echo "======================================================"

# Install Prometheus Node Exporter for system metrics
echo "📦 Installing Prometheus Node Exporter..."
sudo apt update
sudo apt install -y prometheus-node-exporter

# Start and enable Node Exporter
sudo systemctl start prometheus-node-exporter
sudo systemctl enable prometheus-node-exporter

# Create Prometheus configuration
echo "⚙️  Creating Prometheus configuration..."
sudo mkdir -p /etc/prometheus
sudo tee /etc/prometheus/prometheus.yml > /dev/null <<'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'lean-construction'
    static_configs:
      - targets: ['localhost:8000']
EOF

# Install Grafana
echo "📊 Installing Grafana..."
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
sudo apt update
sudo apt install -y grafana

# Start and enable Grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

# Configure Grafana datasources and dashboards
echo "🎨 Configuring Grafana..."
sudo tee /etc/grafana/provisioning/datasources/prometheus.yaml > /dev/null <<'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://localhost:9090
    isDefault: true
EOF

# Create a basic dashboard for Lean Construction AI
sudo mkdir -p /etc/grafana/provisioning/dashboards
sudo tee /etc/grafana/provisioning/dashboards/lean-construction.yaml > /dev/null <<'EOF'
apiVersion: 1

providers:
  - name: 'Lean Construction Dashboards'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /var/lib/grafana/dashboards
EOF

sudo mkdir -p /var/lib/grafana/dashboards
sudo tee /var/lib/grafana/dashboards/system-metrics.json > /dev/null <<'EOF'
{
  "dashboard": {
    "id": null,
    "title": "System Metrics",
    "tags": ["templated"],
    "timezone": "browser",
    "schemaVersion": 16,
    "version": 0,
    "refresh": "25s",
    "panels": [
      {
        "type": "graph",
        "title": "CPU Usage",
        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 9},
        "targets": [
          {
            "expr": "100 - (avg(irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "CPU Usage"
          }
        ]
      },
      {
        "type": "graph",
        "title": "Memory Usage",
        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 9},
        "targets": [
          {
            "expr": "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100",
            "legendFormat": "Memory Usage %"
          }
        ]
      }
    ]
  },
  "overwrite": true
}
EOF

# Restart Grafana to apply configurations
sudo systemctl restart grafana-server

# Set up alerting rules
echo "🔔 Setting up alerting rules..."
sudo mkdir -p /etc/prometheus/rules
sudo tee /etc/prometheus/rules/lean-construction.rules > /dev/null <<'EOF'
groups:
- name: lean-construction-alerts
  rules:
  - alert: HighCPUUsage
    expr: 100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage detected"
      description: "CPU usage is above 80% for more than 5 minutes"

  - alert: HighMemoryUsage
    expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage detected"
      description: "Memory usage is above 85% for more than 5 minutes"

  - alert: LowDiskSpace
    expr: (node_filesystem_size_bytes{fstype!="tmpfs"} - node_filesystem_free_bytes{fstype!="tmpfs"}) / node_filesystem_size_bytes{fstype!="tmpfs"} * 100 > 90
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Low disk space"
      description: "Disk usage is above 90%"
EOF

# Update Prometheus configuration to include rules
sudo tee /etc/prometheus/prometheus.yml > /dev/null <<'EOF'
global:
  scrape_interval: 15s

rule_files:
  - "rules/lean-construction.rules"

scrape_configs:
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'lean-construction'
    static_configs:
      - targets: ['localhost:8000']
EOF

# Restart Prometheus to apply configurations
sudo systemctl restart prometheus-node-exporter

# Install and configure Alertmanager for notifications
echo "📧 Setting up Alertmanager for notifications..."
sudo apt install -y prometheus-alertmanager

# Configure Alertmanager
sudo tee /etc/prometheus/alertmanager.yml > /dev/null <<'EOF'
global:
  smtp_smarthost: 'localhost:25'
  smtp_from: 'alertmanager@constructionaipro.com'
  smtp_require_tls: false

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'email-notifications'

receivers:
- name: 'email-notifications'
  email_configs:
  - to: 'admin@constructionaipro.com'
EOF

# Start and enable Alertmanager
sudo systemctl start prometheus-alertmanager
sudo systemctl enable prometheus-alertmanager

# Update app-monitor.sh to include Prometheus metrics
echo "📈 Updating application monitoring script..."
sudo tee /usr/local/bin/app-monitor.sh > /dev/null <<'EOF'
#!/bin/bash

# Check if PM2 processes are running
if ! pm2 list | grep -q "online"; then
    echo "PM2 processes not running, restarting..."
    pm2 restart all
fi

# Check Nginx
if ! systemctl is-active --quiet nginx; then
    echo "Nginx not running, restarting..."
    sudo systemctl restart nginx
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
    echo "Disk usage is ${DISK_USAGE}%, consider cleanup"
fi

# Check memory usage
MEM_USAGE=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
if (( $(echo "$MEM_USAGE > 90" | bc -l) )); then
    echo "Memory usage is ${MEM_USAGE}%, check processes"
fi

# Check if Prometheus Node Exporter is running
if ! systemctl is-active --quiet prometheus-node-exporter; then
    echo "Prometheus Node Exporter not running, restarting..."
    sudo systemctl restart prometheus-node-exporter
fi

# Check if Grafana is running
if ! systemctl is-active --quiet grafana-server; then
    echo "Grafana not running, restarting..."
    sudo systemctl restart grafana-server
fi

# Check if Alertmanager is running
if ! systemctl is-active --quiet prometheus-alertmanager; then
    echo "Alertmanager not running, restarting..."
    sudo systemctl restart prometheus-alertmanager
fi
EOF

sudo chmod +x /usr/local/bin/app-monitor.sh

echo ""
echo "✅ Enhanced Monitoring Setup Complete!"
echo "===================================="
echo "📊 Monitoring Services:"
echo "   - Prometheus Node Exporter: http://localhost:9100"
echo "   - Grafana: http://localhost:3000 (admin/admin)"
echo "   - Alertmanager: http://localhost:9093"
echo ""
echo "💡 Next steps:"
echo "   1. Access Grafana at http://constructionaipro.com:3000"
echo "   2. Log in with admin/admin and change password"
echo "   3. Configure data sources and dashboards"
echo "   4. Set up email notifications in Alertmanager"
echo "   5. Monitor system metrics through Grafana dashboards"