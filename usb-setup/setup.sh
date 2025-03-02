#!/bin/bash

# USB Server Setup Script
# Run this script as: sudo bash setup.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Starting server setup...${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (sudo bash setup.sh)${NC}"
    exit 1
fi

# Create log file
LOG_FILE="/tmp/server-setup.log"
exec 1> >(tee -a "$LOG_FILE") 2>&1

# Function to log steps
log_step() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# Function to check command success
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Success: $1${NC}"
    else
        echo -e "${RED}✗ Failed: $1${NC}"
        echo "Check $LOG_FILE for details"
        exit 1
    fi
}

# 1. Network Setup
log_step "Setting up network configuration..."

# Backup existing configs
cp /etc/netplan/* /tmp/ 2>/dev/null
rm /etc/netplan/*.yaml 2>/dev/null

# Create new netplan config
cat > /etc/netplan/01-network-config.yaml << EOL
network:
  version: 2
  renderer: networkd
  ethernets:
    enp0s3:
      addresses: [192.168.2.4/24]
      routes:
        - to: default
          via: 192.168.2.1
      nameservers:
        addresses: [192.168.2.1, 8.8.8.8, 8.8.4.4]
      dhcp4: no
EOL

# Set correct permissions
chmod 600 /etc/netplan/01-network-config.yaml
chown root:root /etc/netplan/01-network-config.yaml
check_status "Network configuration file creation"

# Apply network config
netplan generate
netplan apply
check_status "Network configuration application"

# 2. System Updates
log_step "Updating system packages..."
apt update
apt upgrade -y
check_status "System update"

# 3. Install Required Packages
log_step "Installing required packages..."
apt install -y \
    curl \
    wget \
    git \
    build-essential \
    nodejs \
    npm \
    iftop \
    nethogs \
    nload \
    bmon \
    samba \
    samba-common-bin \
    ufw
check_status "Package installation"

# 4. Configure Samba
log_step "Setting up Samba..."
cat > /etc/samba/smb.conf << EOL
[global]
   workgroup = WORKGROUP
   server string = Eco Vehicle Server
   security = user
   map to guest = bad user
   dns proxy = no

[eco-vehicle]
    path = /var/www/eco-vehicle
    browseable = yes
    read only = no
    valid users = banks88ech4un
    create mask = 0644
    directory mask = 0755
EOL

# Create Samba user
(echo "password"; echo "password") | smbpasswd -a banks88ech4un
check_status "Samba configuration"

# 5. Configure Firewall
log_step "Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 445/tcp
ufw allow 139/tcp
ufw allow from 192.168.2.0/24
echo "y" | ufw enable
check_status "Firewall configuration"

# 6. Create Application Directories
log_step "Creating application directories..."
mkdir -p /var/www/eco-vehicle
chown -R banks88ech4un:banks88ech4un /var/www/eco-vehicle
chmod -R 755 /var/www/eco-vehicle
check_status "Directory creation"

# 7. Set up monitoring
log_step "Setting up monitoring..."
cat > /usr/local/bin/monitor.sh << EOL
#!/bin/bash
LOG_DIR="/var/log/eco-vehicle"
mkdir -p \$LOG_DIR

# Network monitoring
echo "=== Network Status ===\$(date)" > \$LOG_DIR/network.log
ip addr show >> \$LOG_DIR/network.log
netstat -tuln >> \$LOG_DIR/network.log

# System monitoring
echo "=== System Status ===\$(date)" > \$LOG_DIR/system.log
df -h >> \$LOG_DIR/system.log
free -h >> \$LOG_DIR/system.log
top -b -n 1 >> \$LOG_DIR/system.log
EOL

chmod +x /usr/local/bin/monitor.sh
check_status "Monitoring setup"

# 8. Create startup script
log_step "Creating startup script..."
cat > /usr/local/bin/startup.sh << EOL
#!/bin/bash
# Restart network
netplan apply

# Start services
systemctl restart smbd
systemctl restart nmbd

# Run monitoring
/usr/local/bin/monitor.sh
EOL

chmod +x /usr/local/bin/startup.sh
check_status "Startup script creation"

# 9. Set up automatic monitoring
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/monitor.sh") | crontab -

# Final checks
log_step "Running final checks..."
systemctl restart smbd nmbd
netplan apply

echo -e "${GREEN}Setup complete! Check $LOG_FILE for detailed logs${NC}"
echo -e "${YELLOW}Server IP: 192.168.2.4${NC}"
echo -e "${YELLOW}Samba share: \\\\192.168.2.4\\eco-vehicle${NC}"

# Print network status
ip addr show
echo -e "${GREEN}Setup finished successfully!${NC}"
