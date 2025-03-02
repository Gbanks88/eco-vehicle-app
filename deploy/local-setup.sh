#!/bin/bash

# Load environment variables
source deploy/local.env

# Check SSH connection
echo "Testing SSH connection..."
ssh -q $UBUNTU_SERVER_USER@$UBUNTU_SERVER_HOST exit
if [ $? -eq 0 ]; then
    echo "SSH connection successful"
else
    echo "Error: Cannot connect via SSH. Please ensure:"
    echo "1. SSH server is running on Ubuntu machine"
    echo "2. Your SSH key is added to the server"
    echo "3. The server's IP address is correct"
    echo ""
    echo "To add your SSH key to the server, run:"
    echo "ssh-copy-id $UBUNTU_SERVER_USER@$UBUNTU_SERVER_HOST"
    exit 1
fi

# Copy deployment files
echo "Copying deployment files..."
scp deploy/setup.sh $UBUNTU_SERVER_USER@$UBUNTU_SERVER_HOST:/tmp/
scp deploy/local.env $UBUNTU_SERVER_USER@$UBUNTU_SERVER_HOST:/tmp/

# Execute setup on remote server
echo "Setting up server..."
ssh $UBUNTU_SERVER_USER@$UBUNTU_SERVER_HOST << 'EOF'
    # Make setup script executable
    chmod +x /tmp/setup.sh

    # Load environment variables
    source /tmp/local.env

    # Run setup script
    sudo /tmp/setup.sh

    # Configure MongoDB for remote access
    sudo sed -i 's/bindIp: 127.0.0.1/bindIp: 0.0.0.0/' /etc/mongod.conf
    sudo systemctl restart mongod

    # Create application log directory
    sudo mkdir -p /var/log/eco-vehicle
    sudo chown -R $USER:$USER /var/log/eco-vehicle

    # Clean up temporary files
    rm /tmp/setup.sh /tmp/local.env

    echo "Server setup complete!"
EOF

# Create local SSH config
echo "Configuring local SSH..."
mkdir -p ~/.ssh
cat >> ~/.ssh/config << EOF
Host eco-vehicle
    HostName $UBUNTU_SERVER_HOST
    User $UBUNTU_SERVER_USER
    Port $UBUNTU_SERVER_PORT
    StrictHostKeyChecking no
EOF

# Test application deployment
echo "Testing deployment..."
./deploy/deploy.sh

echo "Local setup complete! You can now:"
echo "1. SSH to server using: ssh eco-vehicle"
echo "2. Deploy using: ./deploy/deploy.sh"
echo "3. Access the application at: http://$UBUNTU_SERVER_HOST:3000"
