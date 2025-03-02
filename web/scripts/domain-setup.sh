#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Domain configurations
CG4F_SUBDOMAINS=("www" "ev" "3d" "tech" "charging" "parts" "service" "api" "cdn")
JOHNALLENS_SUBDOMAINS=("www" "mens" "womens" "boutique" "sale" "shop" "cart" "checkout" "api" "cdn")

# Enable DNS API
echo -e "${YELLOW}Enabling GCP DNS API...${NC}"
gcloud services enable dns.googleapis.com

# Create DNS zones
echo -e "${YELLOW}Creating DNS zones...${NC}"
gcloud dns managed-zones create cg4f-zone --dns-name="cg4f.online." --description="DNS zone for cg4f.online" || true
gcloud dns managed-zones create johnallens-zone --dns-name="johnallens.com." --description="DNS zone for johnallens.com" || true

# Configure cg4f.online
echo -e "${YELLOW}Configuring cg4f.online DNS records...${NC}"
gcloud dns record-sets create cg4f.online. --rrdatas="75.2.60.5" --ttl=3600 --type=A --zone=cg4f-zone || true
for subdomain in "${CG4F_SUBDOMAINS[@]}"; do
    echo "Creating $subdomain.cg4f.online"
    gcloud dns record-sets create "$subdomain.cg4f.online." --rrdatas="eco-vehicle-app.netlify.app." --ttl=3600 --type=CNAME --zone=cg4f-zone || true
done

# Configure johnallens.com
echo -e "${YELLOW}Configuring johnallens.com DNS records...${NC}"
gcloud dns record-sets create johnallens.com. --rrdatas="75.2.60.5" --ttl=3600 --type=A --zone=johnallens-zone || true
for subdomain in "${JOHNALLENS_SUBDOMAINS[@]}"; do
    echo "Creating $subdomain.johnallens.com"
    gcloud dns record-sets create "$subdomain.johnallens.com." --rrdatas="eco-vehicle-app.netlify.app." --ttl=3600 --type=CNAME --zone=johnallens-zone || true
done

# Add CAA records
echo -e "${YELLOW}Adding CAA records...${NC}"
gcloud dns record-sets create cg4f.online. --rrdatas="0 issue \"letsencrypt.org\"" --ttl=3600 --type=CAA --zone=cg4f-zone || true
gcloud dns record-sets create johnallens.com. --rrdatas="0 issue \"letsencrypt.org\"" --ttl=3600 --type=CAA --zone=johnallens-zone || true

# Verification function
verify_domain() {
    local domain=$1
    echo -e "${YELLOW}Verifying $domain...${NC}"
    
    # DNS lookup
    echo "DNS lookup:"
    dig +short "$domain"
    
    # HTTP response
    echo "HTTP response:"
    curl -I "https://$domain" 2>/dev/null | head -n 1
    
    # SSL verification
    echo "SSL certificate:"
    openssl s_client -connect "$domain":443 -servername "$domain" 2>/dev/null | openssl x509 -noout -dates
    
    echo "----------------------------------------"
}

# Verify all domains
echo -e "${YELLOW}Starting domain verification...${NC}"
verify_domain "cg4f.online"
verify_domain "www.cg4f.online"
verify_domain "johnallens.com"
verify_domain "www.johnallens.com"

# Monitor domains
echo -e "${YELLOW}Setting up domain monitoring...${NC}"
for domain in "cg4f.online" "www.cg4f.online" "johnallens.com" "www.johnallens.com"; do
    # Check DNS propagation
    if dig +short "$domain" > /dev/null; then
        echo -e "${GREEN}✓ DNS propagated for $domain${NC}"
    else
        echo -e "${RED}✗ DNS not propagated for $domain${NC}"
    fi
    
    # Check HTTPS
    if curl -s -o /dev/null -w "%{http_code}" "https://$domain" | grep -q "200\|301\|302"; then
        echo -e "${GREEN}✓ HTTPS working for $domain${NC}"
    else
        echo -e "${RED}✗ HTTPS not working for $domain${NC}"
    fi
done

echo -e "${GREEN}Domain setup and verification complete!${NC}"
