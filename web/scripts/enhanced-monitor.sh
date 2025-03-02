#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
LOG_DIR="/Volumes/Learn_Space/eco_vehicle_project/web/logs"
ALERT_THRESHOLD=2000  # Response time threshold in ms
RETRY_COUNT=3
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

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to check SSL certificate expiry
check_ssl_expiry() {
    local domain=$1
    local expiry_date
    local days_remaining
    
    expiry_date=$(openssl s_client -connect "$domain":443 -servername "$domain" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
    if [ ! -z "$expiry_date" ]; then
        days_remaining=$(( ($(date -j -f "%b %d %H:%M:%S %Y %Z" "$expiry_date" +%s) - $(date +%s)) / 86400 ))
        if [ "$days_remaining" -lt 30 ]; then
            echo -e "${RED}! SSL certificate for $domain expires in $days_remaining days${NC}"
        else
            echo -e "${GREEN}✓ SSL certificate valid for $days_remaining days${NC}"
        fi
    else
        echo -e "${RED}✗ Could not check SSL certificate for $domain${NC}"
    fi
}

# Function to check security headers
check_security_headers() {
    local domain=$1
    local headers
    headers=$(curl -sI "https://$domain")
    
    local issues=()
    
    # Check required security headers
    if ! echo "$headers" | grep -q "Strict-Transport-Security"; then
        issues+=("Missing HSTS header")
    fi
    if ! echo "$headers" | grep -q "Content-Security-Policy"; then
        issues+=("Missing CSP header")
    fi
    if ! echo "$headers" | grep -q "X-Frame-Options"; then
        issues+=("Missing X-Frame-Options header")
    fi
    if ! echo "$headers" | grep -q "X-Content-Type-Options"; then
        issues+=("Missing X-Content-Type-Options header")
    fi
    
    if [ ${#issues[@]} -eq 0 ]; then
        echo -e "${GREEN}✓ All security headers present${NC}"
    else
        echo -e "${RED}✗ Security header issues:${NC}"
        printf '%s\n' "${issues[@]}"
    fi
}

# Function to check response time
check_response_time() {
    local domain=$1
    local response_time
    response_time=$(curl -s -w "%{time_total}\n" -o /dev/null "https://$domain")
    
    response_time_ms=$(echo "$response_time * 1000" | bc)
    if (( $(echo "$response_time_ms > $ALERT_THRESHOLD" | bc -l) )); then
        echo -e "${RED}✗ Slow response time: ${response_time_ms}ms${NC}"
    else
        echo -e "${GREEN}✓ Response time: ${response_time_ms}ms${NC}"
    fi
}

# Function to check DNS records
check_dns_records() {
    local domain=$1
    local ip
    local retry=0
    
    while [ $retry -lt $RETRY_COUNT ]; do
        ip=$(dig +short "$domain" | grep -v "\.$" | head -n 1)
        if [ ! -z "$ip" ]; then
            if [ "$ip" = "75.2.60.5" ]; then
                echo -e "${GREEN}✓ DNS correctly points to Netlify${NC}"
                return 0
            else
                echo -e "${RED}✗ DNS points to wrong IP: $ip${NC}"
                return 1
            fi
        fi
        retry=$((retry + 1))
        sleep 1
    done
    echo -e "${RED}✗ DNS lookup failed after $RETRY_COUNT attempts${NC}"
    return 1
}

# Main monitoring loop
while true; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "\n${YELLOW}Domain Health Check - $timestamp${NC}"
    echo "========================================"
    
    for domain in "${DOMAINS[@]}"; do
        echo -e "\n${YELLOW}Checking $domain${NC}"
        echo "----------------------------------------"
        
        # Create log entry
        log_file="$LOG_DIR/${domain//\//_}.log"
        echo "[$timestamp] Checking $domain" >> "$log_file"
        
        # Perform checks
        check_dns_records "$domain" | tee -a "$log_file"
        check_ssl_expiry "$domain" | tee -a "$log_file"
        check_security_headers "$domain" | tee -a "$log_file"
        check_response_time "$domain" | tee -a "$log_file"
        
        echo "----------------------------------------" | tee -a "$log_file"
    done
    
    echo -e "\n${YELLOW}Sleeping for 5 minutes...${NC}"
    sleep 300
done
