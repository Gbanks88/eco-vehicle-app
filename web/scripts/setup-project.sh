#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Base directory
BASE_DIR="/Volumes/Learn_Space/eco_vehicle_project/web"
cd "$BASE_DIR"

echo -e "${BLUE}Starting project setup...${NC}"

# 1. Environment Setup
echo -e "${YELLOW}Setting up environment...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}Created .env file${NC}"
else
    echo -e "${YELLOW}.env file already exists${NC}"
fi

# 2. Install Dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
npm install

# 3. Database Setup
echo -e "${YELLOW}Setting up database...${NC}"
npm run seed
npm run create-admin

# 4. Build Project
echo -e "${YELLOW}Building project...${NC}"
npm run build

# 5. Security Setup
echo -e "${YELLOW}Configuring security...${NC}"
chmod +x scripts/security-enhancer.sh
./scripts/security-enhancer.sh cg4f.online
./scripts/security-enhancer.sh johnallens.com

# 6. Monitoring Setup
echo -e "${YELLOW}Setting up monitoring...${NC}"
chmod +x scripts/monitor-manager.sh
chmod +x scripts/backup-manager.sh
./scripts/monitor-manager.sh start
./scripts/backup-manager.sh daily

# 7. Game Server Setup
echo -e "${YELLOW}Setting up game servers...${NC}"
cd games/motherboard_explorer
npm install
cd ../..

# 8. Create necessary directories
echo -e "${YELLOW}Creating required directories...${NC}"
mkdir -p logs/metrics
mkdir -p logs/security
mkdir -p logs/games
mkdir -p public/assets/3d
mkdir -p public/assets/games
mkdir -p backups/daily
mkdir -p backups/weekly
mkdir -p backups/monthly

# 9. Set up Netlify
echo -e "${YELLOW}Setting up Netlify...${NC}"
npm install -g netlify-cli
netlify link

# 10. Final checks
echo -e "${YELLOW}Running final checks...${NC}"
npm run lint

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${YELLOW}Please check the setup-log.txt file for any errors${NC}"
