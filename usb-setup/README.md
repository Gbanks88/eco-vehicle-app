# USB Server Setup Instructions

## Prerequisites
- Ubuntu Server installed
- User 'banks88ech4un' created
- Ethernet connection available

## Setup Steps

1. Copy the contents of this USB drive to a temporary directory:
```bash
mkdir /tmp/setup
cp -r /media/ubuntu/USB/* /tmp/setup/
cd /tmp/setup
```

2. Make the script executable:
```bash
chmod +x setup.sh
```

3. Run the setup script:
```bash
sudo bash setup.sh
```

## What This Script Does

1. Network Configuration
   - Sets static IP: 192.168.2.4
   - Configures DNS servers
   - Sets up proper permissions

2. System Setup
   - Updates system packages
   - Installs required software
   - Configures Samba file sharing
   - Sets up firewall rules

3. Monitoring
   - Creates monitoring scripts
   - Sets up automatic logging
   - Configures system checks

## After Installation

1. Verify network connection:
```bash
ip addr show
ping 8.8.8.8
```

2. Check services:
```bash
systemctl status smbd
```

3. Access shared folder from another computer:
- Windows: `\\192.168.2.4\eco-vehicle`
- Mac: `smb://192.168.2.4/eco-vehicle`
- Linux: `smb://192.168.2.4/eco-vehicle`

## Troubleshooting

1. Network Issues:
```bash
sudo netplan apply
sudo systemctl restart networking
```

2. Permission Issues:
```bash
sudo chmod 600 /etc/netplan/01-network-config.yaml
sudo chown root:root /etc/netplan/01-network-config.yaml
```

3. View Logs:
```bash
tail -f /tmp/server-setup.log
```

## Support
For issues, check the logs in `/tmp/server-setup.log`
