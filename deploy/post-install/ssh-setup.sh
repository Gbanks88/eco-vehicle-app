#!/bin/bash

# Create SSH directory if it doesn't exist
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Create SSH config
cat << EOF > ~/.ssh/config
Host eco-server
    HostName 192.168.2.4
    User ubuntu
    Port 22
    IdentityFile ~/.ssh/id_rsa
    ServerAliveInterval 60
    ServerAliveCountMax 3
    ConnectTimeout 10
    StrictHostKeyChecking no
    UserKnownHostsFile ~/.ssh/known_hosts
    ForwardAgent yes
    ForwardX11 yes
    Compression yes
EOF

chmod 600 ~/.ssh/config

# Create SSH key if it doesn't exist
if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
fi

# Try to copy SSH key to server
ssh-copy-id ubuntu@192.168.2.4

# Test connection
echo "Testing SSH connection..."
ssh -T ubuntu@192.168.2.4 "echo 'SSH connection successful'"

echo "SSH setup complete!"
echo "You can now connect using: ssh eco-server"
