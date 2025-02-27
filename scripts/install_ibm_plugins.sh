#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Installing IBM Cloud plugins...${NC}"

# Install DNS plugin
echo -e "\n${GREEN}Installing DNS plugin...${NC}"
ibmcloud plugin install dns

# Install Cloud Internet Services plugin
echo -e "\n${GREEN}Installing CIS plugin...${NC}"
ibmcloud plugin install cis

# Install container-registry plugin
echo -e "\n${GREEN}Installing container-registry plugin...${NC}"
ibmcloud plugin install container-registry

# Install container-service plugin
echo -e "\n${GREEN}Installing container-service plugin...${NC}"
ibmcloud plugin install container-service

# Install key-protect plugin
echo -e "\n${GREEN}Installing key-protect plugin...${NC}"
ibmcloud plugin install key-protect

# Verify installations
echo -e "\n${GREEN}Verifying installations...${NC}"
ibmcloud plugin list

echo -e "\n${GREEN}Plugin installation complete!${NC}"
