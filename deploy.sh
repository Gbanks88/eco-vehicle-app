#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Starting deployment process for CG4F.online..."

# Check if netlify-cli is installed
if ! command -v netlify &> /dev/null; then
    echo "Installing netlify-cli..."
    npm install -g netlify-cli
fi

# Install dependencies
echo -e "\n${GREEN}Installing dependencies...${NC}"
cd web
npm install

# Build the project
echo -e "\n${GREEN}Building the project...${NC}"
npm run build

# Run tests
echo -e "\n${GREEN}Running tests...${NC}"
npm run test || {
    echo -e "${RED}Tests failed! Please fix the issues and try again.${NC}"
    exit 1
}

# Deploy to Netlify
echo -e "\n${GREEN}Deploying to Netlify...${NC}"
netlify deploy --prod

echo -e "\n${GREEN}Deployment complete!${NC}"
echo "Please check the following:"
echo "1. Visit https://cg4f.online to verify the deployment"
echo "2. Test the SysML diagram functionality"
echo "3. Verify Fusion 360 integration"
echo "4. Test the game components"
echo "5. Check real-time synchronization"
