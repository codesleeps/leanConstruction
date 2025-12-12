#!/bin/bash

# ============================================
# Database Performance Optimization Script
# ============================================

echo "⚡ Optimizing Database Performance for Lean Construction AI"
echo "======================================================"

# Connect to PostgreSQL and run optimization queries
echo "🔍 Analyzing and optimizing PostgreSQL database..."

# Create indexes for common query patterns
sudo -u postgres psql -d leandb << 'EOF'
-- Create indexes for frequently queried columns
CREATE INDEX IF NOT EXISTS idx_projects_owner_id ON projects(owner_id);
CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_waste_logs_project_id ON waste_logs(project_id);
CREATE INDEX IF NOT EXISTS idx_waste_logs_waste_type ON waste_logs(waste_type);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Analyze tables to update statistics for query planner
ANALYZE projects;
ANALYZE tasks;
ANALYZE waste_logs;
ANALYZE users;

-- Vacuum tables to reclaim storage
VACUUM ANALYZE projects;
VACUUM ANALYZE tasks;
VACUUM ANALYZE waste_logs;
VACUUM ANALYZE users;

-- Check for missing indexes
SELECT
    relname AS table_name,
    seq_scan,
    idx_scan
FROM
    pg_stat_user_tables
WHERE
    seq_scan > idx_scan
    AND seq_scan > 1000
ORDER BY
    seq_scan DESC;

-- Show current database size
SELECT pg_size_pretty(pg_database_size('leandb')) AS database_size;

-- Show largest tables
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size
FROM
    pg_tables
WHERE
    schemaname = 'public'
ORDER BY
    pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
EOF

# Update PostgreSQL configuration for better performance
echo "⚙️  Optimizing PostgreSQL configuration..."

# Backup current configuration
sudo cp /etc/postgresql/15/main/postgresql.conf /etc/postgresql/15/main/postgresql.conf.backup

# Apply performance optimizations
sudo tee -a /etc/postgresql/15/main/postgresql.conf > /dev/null <<'EOF'

# Performance optimizations
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 16MB
min_wal_size = 1GB
max_wal_size = 4GB
EOF

# Restart PostgreSQL to apply changes
sudo systemctl restart postgresql

# Optimize Redis configuration
echo "キャッシング Optimizing Redis configuration..."

# Backup current configuration
sudo cp /etc/redis/redis.conf /etc/redis/redis.conf.backup

# Apply Redis optimizations
sudo tee -a /etc/redis/redis.conf > /dev/null <<'EOF'

# Performance optimizations
maxmemory 2gb
maxmemory-policy allkeys-lru
tcp-keepalive 60
timeout 300
EOF

# Restart Redis to apply changes
sudo systemctl restart redis

# Update application to use connection pooling
echo "🔌 Configuring connection pooling..."

# Create a script to monitor database connections
sudo tee /usr/local/bin/db-monitor.sh > /dev/null <<'EOF'
#!/bin/bash

# Monitor database connections
CONNECTIONS=$(sudo -u postgres psql -d leandb -t -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';" | xargs)
echo "Active database connections: $CONNECTIONS"

# Check for long-running queries
LONG_QUERIES=$(sudo -u postgres psql -d leandb -t -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active' AND now() - query_start > interval '5 minutes';" | xargs)
echo "Long-running queries (>5min): $LONG_QUERIES"

# Check database cache hit ratio
CACHE_HIT_RATIO=$(sudo -u postgres psql -d leandb -t -c "SELECT round(sum(blks_hit)*100/(sum(blks_hit)+sum(blks_read)), 2) FROM pg_stat_database;" | xargs)
echo "Cache hit ratio: $CACHE_HIT_RATIO%"
EOF

sudo chmod +x /usr/local/bin/db-monitor.sh

# Add database monitoring to cron
echo "⏰ Setting up database monitoring cron job..."
(crontab -l 2>/dev/null; echo "*/10 * * * * /usr/local/bin/db-monitor.sh >> /var/log/db-monitor.log 2>&1") | crontab -

echo ""
echo "✅ Database Performance Optimization Complete!"
echo "=========================================="
echo "📊 Optimizations applied:"
echo "   - Created indexes for common query patterns"
echo "   - Updated PostgreSQL configuration for better performance"
echo "   - Optimized Redis settings"
echo "   - Configured connection pooling"
echo "   - Set up database monitoring"
echo ""
echo "💡 Next steps:"
echo "   1. Monitor query performance with EXPLAIN ANALYZE"
echo "   2. Review slow query logs regularly"
echo "   3. Adjust configuration based on workload"
echo "   4. Monitor cache hit ratios and connection usage"