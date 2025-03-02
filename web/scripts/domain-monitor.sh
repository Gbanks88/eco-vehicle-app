#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Domains to monitor
DOMAINS=(
    "cg4f.online"
    "www.cg4f.online"
    "ev.cg4f.online"
    "3d.cg4f.online"
    "tech.cg4f.online"
    "charging.cg4f.online"
    "parts.cg4f.online"
    "service.cg4f.online"
    "api.cg4f.online"
    "cdn.cg4f.online"
    "johnallens.com"
    "www.johnallens.com"
    "mens.johnallens.com"
    "womens.johnallens.com"
    "boutique.johnallens.com"
    "sale.johnallens.com"
    "shop.johnallens.com"
    "cart.johnallens.com"
    "checkout.johnallens.com"
    "api.johnallens.com"
    "cdn.johnallens.com"
)

# Function to check domain health
check_domain() {
    local domain=$1
    local status_code
    local ssl_expiry
    
    echo -e "${YELLOW}Checking $domain...${NC}"
    
    # Check DNS
    if dig +short "$domain" > /dev/null; then
        echo -e "${GREEN}✓ DNS resolved${NC}"
    else
        echo -e "${RED}✗ DNS failed${NC}"
    fi
    
    # Check HTTPS status
    status_code=$(curl -s -o /dev/null -w "%{http_code}" "https://$domain")
    if [[ "$status_code" =~ ^(200|301|302)$ ]]; then
        echo -e "${GREEN}✓ HTTPS Status: $status_code${NC}"
    else
        echo -e "${RED}✗ HTTPS Status: $status_code${NC}"
    fi
    
    # Check SSL certificate
    ssl_expiry=$(openssl s_client -connect "$domain":443 -servername "$domain" 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
    if [ ! -z "$ssl_expiry" ]; then
        echo -e "${GREEN}✓ SSL valid until: $ssl_expiry${NC}"
    else
        echo -e "${RED}✗ SSL certificate check failed${NC}"
    fi
    
    # Check response time
    local response_time
    response_time=$(curl -s -w "%{time_total}\n" -o /dev/null "https://$domain")
    if (( $(echo "$response_time < 2" | bc -l) )); then
        echo -e "${GREEN}✓ Response time: ${response_time}s${NC}"
    else
        echo -e "${RED}✗ Slow response time: ${response_time}s${NC}"
    fi
    
    echo "----------------------------------------"
}

# Main monitoring loop
while true; do
    echo -e "${YELLOW}Starting domain health check - $(date)${NC}"
    echo "========================================"
    
    for domain in "${DOMAINS[@]}"; do
        check_domain "$domain"
    done
    
    echo -e "${YELLOW}Health check complete - waiting 5 minutes${NC}"
    echo "========================================"
    sleep 300
done
