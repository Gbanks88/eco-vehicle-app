#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Base directories
BASE_DIR="/Volumes/Learn_Space/eco_vehicle_project/web"
LOG_DIR="$BASE_DIR/logs"
CONFIG_FILE="$BASE_DIR/scripts/monitor-config.json"

# Create required directories
mkdir -p "$LOG_DIR/alerts"
mkdir -p "$LOG_DIR/metrics"
mkdir -p "$LOG_DIR/performance"

# Load configuration
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}Error: Configuration file not found${NC}"
    exit 1
fi

# Function to check 3D performance
check_3d_performance() {
    local domain=$1
    local threshold=$2
    local fps
    
    # Simulate WebGL performance check
    fps=$(curl -s "https://$domain/api/diagnostics/webgl" | jq '.fps')
    
    if [ -z "$fps" ] || [ "$fps" -lt "$threshold" ]; then
        echo -e "${RED}✗ 3D Performance below threshold: ${fps}fps${NC}"
        return 1
    else
        echo -e "${GREEN}✓ 3D Performance: ${fps}fps${NC}"
        return 0
    fi
}

# Function to check API endpoints
check_api_endpoints() {
    local domain=$1
    local endpoints=("$@")
    local failed=0
    
    echo "Checking API endpoints:"
    for endpoint in "${endpoints[@]}"; do
        local response
        response=$(curl -s -o /dev/null -w "%{http_code}" "https://$domain$endpoint")
        
        if [ "$response" = "200" ]; then
            echo -e "${GREEN}✓ $endpoint${NC}"
        else
            echo -e "${RED}✗ $endpoint (HTTP $response)${NC}"
            failed=$((failed + 1))
        fi
    done
    
    return $failed
}

# Function to check e-commerce functionality
check_ecommerce() {
    local domain=$1
    local cart_time
    local checkout_time
    
    echo "Testing e-commerce functions:"
    
    # Test cart operations
    cart_time=$(curl -s -w "%{time_total}\n" -o /dev/null "https://$domain/api/cart/test")
    if (( $(echo "$cart_time > 2.0" | bc -l) )); then
        echo -e "${RED}✗ Cart response slow: ${cart_time}s${NC}"
    else
        echo -e "${GREEN}✓ Cart response: ${cart_time}s${NC}"
    fi
    
    # Test checkout flow
    checkout_time=$(curl -s -w "%{time_total}\n" -o /dev/null "https://$domain/api/checkout/test")
    if (( $(echo "$checkout_time > 5.0" | bc -l) )); then
        echo -e "${RED}✗ Checkout response slow: ${checkout_time}s${NC}"
    else
        echo -e "${GREEN}✓ Checkout response: ${checkout_time}s${NC}"
    fi
}

# Function to collect metrics
collect_metrics() {
    local domain=$1
    local timestamp=$(date +%s)
    local metrics_file="$LOG_DIR/metrics/${domain//\//_}_$(date +%Y%m%d).csv"
    
    # Create headers if file doesn't exist
    if [ ! -f "$metrics_file" ]; then
        echo "timestamp,response_time,ssl_days_remaining,security_score,uptime" > "$metrics_file"
    fi
    
    # Collect metrics
    local response_time=$(curl -s -w "%{time_total}\n" -o /dev/null "https://$domain")
    local ssl_days=$(openssl s_client -connect "$domain":443 -servername "$domain" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
    local security_score=100
    local uptime=1
    
    # Calculate security score
    if ! curl -sI "https://$domain" | grep -q "Strict-Transport-Security"; then
        security_score=$((security_score - 20))
    fi
    if ! curl -sI "https://$domain" | grep -q "Content-Security-Policy"; then
        security_score=$((security_score - 20))
    fi
    
    # Save metrics
    echo "$timestamp,$response_time,$ssl_days,$security_score,$uptime" >> "$metrics_file"
}

# Function to send alerts
send_alert() {
    local domain=$1
    local issue=$2
    local alert_file="$LOG_DIR/alerts/$(date +%Y%m%d)_${domain//\//_}.log"
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $domain: $issue" >> "$alert_file"
    
    # Here you would implement actual alert sending (email, Slack, etc.)
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚨 Alert for $domain: $issue\"}" \
            "$SLACK_WEBHOOK_URL"
    fi
}

# Main monitoring loop
echo -e "${BLUE}Starting advanced monitoring system...${NC}"
echo "Configuration loaded from: $CONFIG_FILE"

while true; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "\n${YELLOW}Comprehensive Health Check - $timestamp${NC}"
    echo "================================================"
    
    # Read and process configuration
    while IFS= read -r domain; do
        echo -e "\n${YELLOW}Analyzing $domain${NC}"
        echo "----------------------------------------"
        
        # Get domain type from config
        domain_type=$(jq -r ".domains.\"$domain\".type" "$CONFIG_FILE")
        
        # Perform basic checks
        check_dns_records "$domain"
        check_ssl_expiry "$domain"
        check_security_headers "$domain"
        
        # Perform type-specific checks
        case $domain_type in
            "service")
                check_3d_performance "$domain" 30
                ;;
            "api")
                endpoints=$(jq -r ".domains.\"$domain\".endpoints[]" "$CONFIG_FILE")
                check_api_endpoints "$domain" $endpoints
                ;;
            "ecommerce")
                check_ecommerce "$domain"
                ;;
        esac
        
        # Collect metrics
        collect_metrics "$domain"
        
        echo "----------------------------------------"
    done < <(jq -r '.domains | keys[]' "$CONFIG_FILE")
    
    # Sleep for configured interval
    interval=$(jq -r '.global.checkInterval' "$CONFIG_FILE")
    echo -e "\n${BLUE}Sleeping for $interval seconds...${NC}"
    sleep "$interval"
done
