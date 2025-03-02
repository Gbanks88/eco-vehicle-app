#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Expected Netlify IP
NETLIFY_IP="75.2.60.5"

# Domain lists
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

# Function to check SSL certificate
check_ssl() {
    local domain=$1
    local ssl_info
    ssl_info=$(openssl s_client -connect "$domain":443 -servername "$domain" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
    if [ ! -z "$ssl_info" ]; then
        echo -e "${GREEN}✓ SSL certificate found for $domain${NC}"
        echo "$ssl_info"
    else
        echo -e "${RED}✗ No SSL certificate found for $domain${NC}"
    fi
}

# Function to check DNS records
check_dns() {
    local domain=$1
    local ip
    ip=$(dig +short "$domain" | grep -v "\.$" | head -n 1)
    
    if [ -z "$ip" ]; then
        echo -e "${RED}✗ No DNS A record found for $domain${NC}"
    elif [ "$ip" = "$NETLIFY_IP" ]; then
        echo -e "${GREEN}✓ DNS points to Netlify ($ip)${NC}"
    else
        echo -e "${YELLOW}! DNS points to $ip (expected: $NETLIFY_IP)${NC}"
    fi
    
    # Check CNAME if it's a subdomain
    if [[ "$domain" == *"."* ]]; then
        local cname
        cname=$(dig +short CNAME "$domain")
        if [[ "$cname" == *"netlify"* ]]; then
            echo -e "${GREEN}✓ CNAME record correctly points to Netlify${NC}"
        else
            echo -e "${YELLOW}! CNAME record: $cname${NC}"
        fi
    fi
}

# Function to check HTTP response
check_http() {
    local domain=$1
    local http_code
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "https://$domain")
    
    if [[ "$http_code" =~ ^(200|301|302)$ ]]; then
        echo -e "${GREEN}✓ HTTPS response: $http_code${NC}"
    else
        echo -e "${RED}✗ HTTPS response: $http_code${NC}"
    fi
}

# Function to check security headers
check_security_headers() {
    local domain=$1
    local headers
    headers=$(curl -sI "https://$domain")
    
    echo "Security Headers:"
    if echo "$headers" | grep -q "Strict-Transport-Security"; then
        echo -e "${GREEN}✓ HSTS enabled${NC}"
    else
        echo -e "${RED}✗ HSTS missing${NC}"
    fi
    
    if echo "$headers" | grep -q "Content-Security-Policy"; then
        echo -e "${GREEN}✓ CSP enabled${NC}"
    else
        echo -e "${RED}✗ CSP missing${NC}"
    fi
    
    if echo "$headers" | grep -q "X-Frame-Options"; then
        echo -e "${GREEN}✓ X-Frame-Options set${NC}"
    else
        echo -e "${RED}✗ X-Frame-Options missing${NC}"
    fi
}

# Main verification loop
echo -e "${YELLOW}Starting domain verification...${NC}"
echo "======================================"

for domain in "${DOMAINS[@]}"; do
    echo -e "\n${YELLOW}Checking $domain${NC}"
    echo "----------------------------------------"
    check_dns "$domain"
    check_ssl "$domain"
    check_http "$domain"
    check_security_headers "$domain"
    echo "----------------------------------------"
done

echo -e "\n${YELLOW}Verification complete!${NC}"
