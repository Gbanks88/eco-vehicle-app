#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
APP_NAME="eco-vehicle-app"
REDIS_SERVICE="eco-vehicle-redis"
CLOUDANT_SERVICE="eco-vehicle-cloudant"
REGION="us-south"  # IBM Cloud region

echo "Deploying Eco Vehicle Project to IBM Cloud..."

# Check if IBM Cloud CLI is installed
if ! command -v ibmcloud &> /dev/null; then
    echo -e "${RED}IBM Cloud CLI not found. Installing...${NC}"
    curl -fsSL https://clis.cloud.ibm.com/install/osx | sh
fi

# Login to IBM Cloud
echo "Logging in to IBM Cloud..."
ibmcloud login -r $REGION

# Target Cloud Foundry organization and space
echo "Selecting Cloud Foundry org and space..."
ibmcloud target --cf

# Create services if they don't exist
echo "Setting up required services..."

# Create Redis service
if ! ibmcloud service show $REDIS_SERVICE &> /dev/null; then
    echo "Creating Redis service..."
    ibmcloud service create databases-for-redis standard $REDIS_SERVICE
fi

# Create Cloudant service
if ! ibmcloud service show $CLOUDANT_SERVICE &> /dev/null; then
    echo "Creating Cloudant service..."
    ibmcloud service create cloudantnosqldb lite $CLOUDANT_SERVICE
fi

# Wait for services to be ready
echo "Waiting for services to be ready..."
ibmcloud service show $REDIS_SERVICE
ibmcloud service show $CLOUDANT_SERVICE

# Set environment variables from .env file
echo "Setting environment variables..."
if [ -f .env ]; then
    while IFS='=' read -r key value; do
        if [ ! -z "$key" ] && [ ! -z "$value" ]; then
            ibmcloud cf set-env $APP_NAME $key $value
        fi
    done < .env
fi

# Push the application
echo "Pushing application to IBM Cloud..."
ibmcloud cf push

# Check if the deployment was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Deployment successful!${NC}"
    echo "Your application is now running at: https://eco-vehicle.cg4f.online"
    
    # Show application status
    ibmcloud cf app $APP_NAME
    
    # Show bound services
    echo -e "\nBound Services:"
    ibmcloud cf services | grep $APP_NAME
else
    echo -e "${RED}Deployment failed. Check the logs above for errors.${NC}"
    exit 1
fi
