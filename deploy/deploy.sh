#!/bin/bash

# Load configuration
source .env

# Check required environment variables
if [ -z "$UBUNTU_SERVER_HOST" ] || [ -z "$UBUNTU_SERVER_USER" ] || [ -z "$DOMAIN_NAME" ]; then
    echo "Error: Missing required environment variables"
    exit 1
fi

# Build the application
echo "Building application..."
npm run build

# Create deployment archive
echo "Creating deployment archive..."
tar -czf deploy.tar.gz \
    .next \
    package.json \
    package-lock.json \
    public \
    deploy/config.js \
    ecosystem.config.js

# Copy files to server
echo "Copying files to server..."
scp deploy.tar.gz $UBUNTU_SERVER_USER@$UBUNTU_SERVER_HOST:/var/www/eco-vehicle/

# Deploy on server
echo "Deploying on server..."
ssh $UBUNTU_SERVER_USER@$UBUNTU_SERVER_HOST << 'EOF'
    cd /var/www/eco-vehicle
    tar -xzf deploy.tar.gz
    npm install --production
    
    # Start/restart PM2 process
    if pm2 list | grep -q "eco-vehicle-app"; then
        pm2 reload eco-vehicle-app
    else
        pm2 start ecosystem.config.js
    fi
    
    # Save PM2 process list
    pm2 save
    
    # Clean up
    rm deploy.tar.gz
EOF

# Configure SSL if not already set up
if [ "$SETUP_SSL" = "true" ]; then
    echo "Configuring SSL..."
    ssh $UBUNTU_SERVER_USER@$UBUNTU_SERVER_HOST << EOF
        sudo certbot --nginx \
            -d $DOMAIN_NAME \
            -d www.$DOMAIN_NAME \
            --non-interactive \
            --agree-tos \
            --email $SSL_EMAIL
EOF
fi

# Verify deployment
echo "Verifying deployment..."
curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN_NAME

echo "Deployment complete!"
