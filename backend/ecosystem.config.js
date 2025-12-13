module.exports = {
  apps: [{
    name: 'lean-construction-api',
    script: '/var/www/lean-construction/venv/bin/uvicorn',
    args: 'app.main_lite:app --host 0.0.0.0 --port 8000',
    cwd: '/var/www/lean-construction',
    interpreter: 'none',
    env: {
      PYTHONPATH: '/var/www/lean-construction',
      // DATABASE_URL and SECRET_KEY are now loaded from .env file
      // ENVIRONMENT: 'production'
    },
    instances: 1,
    exec_mode: 'fork',
    watch: false,
    max_memory_restart: '1G',
    error_file: '/var/www/lean-construction/logs/pm2-error.log',
    out_file: '/var/www/lean-construction/logs/pm2-out.log',
    time: true
  }]
};