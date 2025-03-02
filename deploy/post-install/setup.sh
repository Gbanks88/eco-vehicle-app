#!/bin/bash

# Post-installation setup script for Ubuntu server
# Run this after fresh Ubuntu installation

# Set script to exit on error
set -e

echo "Starting post-installation setup..."

# 1. Configure Network
echo "Configuring network..."
sudo cp network.yaml /etc/netplan/00-installer-config.yaml
sudo netplan generate
sudo netplan apply

# 2. Update System
echo "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# 3. Install Essential Packages
echo "Installing essential packages..."
sudo apt install -y \
    curl \
    wget \
    git \
    vim \
    net-tools \
    htop \
    ufw \
    fail2ban \
    build-essential \
    software-properties-common

# 4. Configure SSH
echo "Configuring SSH..."
sudo cp sshd_config /etc/ssh/sshd_config
sudo systemctl restart ssh

# 5. Configure Firewall
echo "Configuring firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw allow 3000/tcp # Node.js application
sudo ufw allow from 192.168.2.0/24 # Allow local network
sudo ufw --force enable

# 6. Configure Fail2ban
echo "Configuring Fail2ban..."
sudo cp fail2ban.conf /etc/fail2ban/jail.local
sudo systemctl restart fail2ban

# 7. Set up Node.js
echo "Setting up Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pm2

# 8. Create Application Directory
echo "Creating application directory..."
sudo mkdir -p /var/www/eco-vehicle
sudo chown -R $USER:$USER /var/www/eco-vehicle

# 9. Configure Project Environment
echo "Configuring project environment..."
cp env.production /var/www/eco-vehicle/.env

# 10. Set up MongoDB
echo "Setting up MongoDB..."
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod

# 11. Set up SQL Server
echo "Setting up SQL Server dependencies..."
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt update
sudo ACCEPT_EULA=Y apt install -y msodbcsql18 mssql-tools18

# 12. Install and configure Nginx
echo "Setting up Nginx..."
sudo apt install -y nginx
sudo cp nginx.conf /etc/nginx/sites-available/eco-vehicle
sudo ln -s /etc/nginx/sites-available/eco-vehicle /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# 13. Set up SSL (self-signed for development)
echo "Setting up SSL certificate..."
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/eco-vehicle.key \
    -out /etc/ssl/certs/eco-vehicle.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=192.168.2.4"

# 14. Set up log directories
echo "Setting up log directories..."
sudo mkdir -p /var/log/eco-vehicle
sudo chown -R $USER:$USER /var/log/eco-vehicle

# 15. Configure system limits
echo "Configuring system limits..."
echo "* soft nofile 65536
* hard nofile 65536
* soft nproc 32768
* hard nproc 32768" | sudo tee -a /etc/security/limits.conf

# 16. Set up backup directory
echo "Setting up backup directory..."
sudo mkdir -p /var/backups/eco-vehicle
sudo chown -R $USER:$USER /var/backups/eco-vehicle

# 17. Create maintenance scripts
echo "Setting up maintenance scripts..."
mkdir -p ~/scripts
cp maintenance/* ~/scripts/
chmod +x ~/scripts/*

# Final steps
echo "Post-installation setup complete!"
echo "Next steps:"
echo "1. Deploy application code"
echo "2. Start the application with PM2"
echo "3. Monitor the logs"
echo ""
echo "Server IP: 192.168.2.4"
echo "SSH: ssh ubuntu@192.168.2.4"
echo "Application URL: http://192.168.2.4"
echo "Secure URL: https://192.168.2.4"

# Print system status
echo ""
echo "System Status:"
echo "-------------"
echo "Network:"
ip addr show eno1
echo ""
echo "Services:"
systemctl status nginx --no-pager
systemctl status mongod --no-pager
echo ""
echo "Firewall:"
sudo ufw status
