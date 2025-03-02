#!/bin/bash

# Install required packages
sudo apt update
sudo apt install -y ifenslave

# Enable kernel module
sudo modprobe bonding
echo "bonding" | sudo tee -a /etc/modules

# Copy network configuration
sudo cp network-config.yaml /etc/netplan/01-netcfg.yaml

# Apply network configuration
sudo netplan generate
sudo netplan apply

# Check bond status
echo "Bond Status:"
cat /proc/net/bonding/bond0

# Show network status
ip addr show bond0
