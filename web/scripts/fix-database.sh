#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Base directory
BASE_DIR="/Volumes/Learn_Space/eco_vehicle_project/web"

echo -e "${BLUE}Starting database fix...${NC}"

# Check MongoDB installation
if ! command -v mongod &> /dev/null; then
    echo -e "${RED}MongoDB not found. Installing...${NC}"
    brew tap mongodb/brew
    brew install mongodb-community
fi

# Start MongoDB service
echo -e "${YELLOW}Starting MongoDB service...${NC}"
brew services start mongodb-community

# Wait for MongoDB to start
echo -e "${YELLOW}Waiting for MongoDB to start...${NC}"
sleep 5

# Create database and user
echo -e "${YELLOW}Setting up database...${NC}"
mongosh --eval '
  db = db.getSiblingDB("eco_vehicle_db");
  
  // Create admin user if not exists
  if (!db.getUser("admin")) {
    db.createUser({
      user: "admin",
      pwd: "your-secure-password",
      roles: ["readWrite", "dbAdmin"]
    });
  }
  
  // Create collections
  db.createCollection("users");
  db.createCollection("vehicles");
  db.createCollection("games");
  db.createCollection("metrics");
'

# Update .env file with MongoDB URI
echo -e "${YELLOW}Updating MongoDB connection string...${NC}"
if grep -q "MONGODB_URI" "$BASE_DIR/.env"; then
    sed -i '' 's|MONGODB_URI=.*|MONGODB_URI=mongodb://localhost:27017/eco_vehicle_db|g' "$BASE_DIR/.env"
else
    echo "MONGODB_URI=mongodb://localhost:27017/eco_vehicle_db" >> "$BASE_DIR/.env"
fi

# Run database seeding
echo -e "${YELLOW}Running database seed...${NC}"
cd "$BASE_DIR"
npm run seed

# Create admin user
echo -e "${YELLOW}Creating admin user...${NC}"
npm run create-admin

echo -e "${GREEN}Database setup complete!${NC}"
