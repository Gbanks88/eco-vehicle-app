#!/bin/bash

# Configure local development environment to use local mirrors

# NPM Configuration
npm config set registry http://192.168.2.4:4873/

# PIP Configuration
mkdir -p ~/.pip
cat << EOF > ~/.pip/pip.conf
[global]
index-url = http://192.168.2.4:3141/root/pypi/+simple/
trusted-host = 192.168.2.4
EOF

# Docker Configuration
cat << EOF | sudo tee /etc/docker/daemon.json
{
  "registry-mirrors": ["http://192.168.2.4:5000"],
  "insecure-registries": ["192.168.2.4:5000"]
}
EOF
sudo systemctl restart docker

# Git Configuration
git config --global url."http://192.168.2.4:3000/".insteadOf "https://github.com/"

# Add environment variables
cat << EOF >> ~/.bashrc
# Local Mirror Configuration
export NPM_CONFIG_REGISTRY=http://192.168.2.4:4873/
export PIP_INDEX_URL=http://192.168.2.4:3141/root/pypi/+simple/
export DOCKER_REGISTRY=192.168.2.4:5000
export GIT_MIRROR=http://192.168.2.4:3000/
EOF

echo "Client configuration complete!"
echo "Your development environment is now configured to use local mirrors."
