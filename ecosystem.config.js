const config = require('./deploy/config');

module.exports = {
  apps: [{
    name: config.server.pm2Name,
    script: 'node_modules/next/dist/bin/next',
    args: 'start',
    instances: config.pm2.instances,
    exec_mode: config.pm2.exec_mode,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      PORT: config.nginx.proxyPort
    },
    error_file: '/var/log/eco-vehicle/error.log',
    out_file: '/var/log/eco-vehicle/out.log',
    merge_logs: true,
    log_date_format: 'YYYY-MM-DD HH:mm:ss'
  }]
};
