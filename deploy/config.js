module.exports = {
  // Server Configuration
  server: {
    host: process.env.UBUNTU_SERVER_HOST,
    username: process.env.UBUNTU_SERVER_USER,
    port: process.env.UBUNTU_SERVER_PORT || 22,
    deployPath: '/var/www/eco-vehicle',
    pm2Name: 'eco-vehicle-app'
  },

  // Database Configuration
  database: {
    mongodb: {
      url: process.env.MONGODB_URI,
      backupPath: '/var/backups/mongodb'
    },
    sql: {
      host: process.env.SQL_SERVER,
      user: process.env.SQL_USER,
      password: process.env.SQL_PASSWORD,
      database: process.env.SQL_DATABASE
    }
  },

  // SSL Configuration
  ssl: {
    enabled: true,
    email: process.env.SSL_EMAIL,
    domain: process.env.DOMAIN_NAME,
    staging: process.env.NODE_ENV !== 'production'
  },

  // Nginx Configuration
  nginx: {
    serverName: process.env.DOMAIN_NAME,
    proxyPort: 3000,
    sslPath: '/etc/letsencrypt/live'
  },

  // PM2 Configuration
  pm2: {
    instances: 'max',
    exec_mode: 'cluster'
  },

  // Backup Configuration
  backup: {
    enabled: true,
    frequency: '0 0 * * *', // Daily at midnight
    retention: 7 // Days to keep backups
  }
};
