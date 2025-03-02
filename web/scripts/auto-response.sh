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

# Function to reload Netlify configuration
reload_netlify_config() {
    local domain=$1
    echo "Reloading Netlify configuration for $domain..."
    netlify deploy --prod
}

# Function to refresh SSL certificate
refresh_ssl() {
    local domain=$1
    echo "Requesting new SSL certificate for $domain..."
    netlify sites:enable-https "$domain"
}

# Function to update security headers
update_security_headers() {
    local domain=$1
    echo "Updating security headers for $domain..."
    
    # Backup current headers
    cp "$BASE_DIR/public/_headers" "$BASE_DIR/public/_headers.backup"
    
    # Update headers with stricter policies
    sed -i '' 's/Content-Security-Policy:.*/Content-Security-Policy: default-src '\''self'\''; script-src '\''self'\'' '\''unsafe-inline'\''; style-src '\''self'\'' '\''unsafe-inline'\'';/' "$BASE_DIR/public/_headers"
    
    # Deploy changes
    netlify deploy --prod
}

# Function to mitigate potential attacks
mitigate_attack() {
    local domain=$1
    local attack_type=$2
    
    echo "Mitigating $attack_type attack on $domain..."
    
    case $attack_type in
        "dos")
            # Enable Netlify DDoS protection
            curl -X POST "https://api.netlify.com/api/v1/sites/$NETLIFY_SITE_ID/ddos" \
                -H "Authorization: Bearer $NETLIFY_AUTH_TOKEN"
            ;;
        "injection")
            # Update CSP headers to be more restrictive
            update_security_headers "$domain"
            ;;
        "brute_force")
            # Implement rate limiting
            echo "/*" >> "$BASE_DIR/public/_headers"
            echo "  X-RateLimit-Limit: 100" >> "$BASE_DIR/public/_headers"
            echo "  X-RateLimit-Remaining: 100" >> "$BASE_DIR/public/_headers"
            netlify deploy --prod
            ;;
    esac
}

# Function to optimize performance
optimize_performance() {
    local domain=$1
    echo "Optimizing performance for $domain..."
    
    # Enable caching
    echo "/*" >> "$BASE_DIR/public/_headers"
    echo "  Cache-Control: public, max-age=3600" >> "$BASE_DIR/public/_headers"
    echo "  CDN-Cache-Control: public, max-age=31536000" >> "$BASE_DIR/public/_headers"
    
    # Deploy changes
    netlify deploy --prod
}

# Function to handle alerts
handle_alert() {
    local domain=$1
    local issue=$2
    local severity=$3
    
    echo -e "${YELLOW}Handling alert for $domain: $issue (Severity: $severity)${NC}"
    
    case $issue in
        *"SSL certificate"*)
            refresh_ssl "$domain"
            ;;
        *"security headers"*)
            update_security_headers "$domain"
            ;;
        *"performance"*)
            optimize_performance "$domain"
            ;;
        *"attack detected"*)
            mitigate_attack "$domain" "dos"
            ;;
        *"brute force"*)
            mitigate_attack "$domain" "brute_force"
            ;;
        *"injection attempt"*)
            mitigate_attack "$domain" "injection"
            ;;
    esac
    
    # Log the action taken
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] AUTO-RESPONSE: Handled $issue for $domain" >> "$LOG_DIR/auto-response.log"
}

# Function to analyze metrics and trigger responses
analyze_metrics() {
    local domain=$1
    local metrics_file="$LOG_DIR/metrics/${domain//\//_}_$(date +%Y%m%d).csv"
    
    if [ -f "$metrics_file" ]; then
        # Get latest metrics
        local latest=$(tail -n 1 "$metrics_file")
        
        # Parse metrics
        local response_time=$(echo "$latest" | cut -d',' -f2)
        local ssl_days=$(echo "$latest" | cut -d',' -f3)
        local security_score=$(echo "$latest" | cut -d',' -f4)
        
        # Check thresholds and respond
        if (( $(echo "$response_time > 2.0" | bc -l) )); then
            handle_alert "$domain" "slow response time" "warning"
        fi
        
        if [ "$ssl_days" -lt 30 ]; then
            handle_alert "$domain" "SSL certificate expiring soon" "warning"
        fi
        
        if [ "$security_score" -lt 70 ]; then
            handle_alert "$domain" "low security score" "critical"
        fi
    fi
}

# Main loop
echo -e "${BLUE}Starting automated response system...${NC}"

while true; do
    echo -e "\n${YELLOW}Checking for issues - $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    
    # Process each domain
    while IFS= read -r domain; do
        echo -e "\n${YELLOW}Analyzing $domain${NC}"
        analyze_metrics "$domain"
    done < <(jq -r '.domains | keys[]' "$CONFIG_FILE")
    
    # Check for new alerts
    latest_alerts=$(find "$LOG_DIR/alerts" -type f -mmin -5)
    if [ ! -z "$latest_alerts" ]; then
        while IFS= read -r alert_file; do
            while IFS= read -r alert; do
                if [[ $alert =~ \[(.*?)\]\ (.*?):\ (.*) ]]; then
                    domain="${BASH_REMATCH[2]}"
                    issue="${BASH_REMATCH[3]}"
                    handle_alert "$domain" "$issue" "warning"
                fi
            done < "$alert_file"
        done <<< "$latest_alerts"
    fi
    
    echo -e "${BLUE}Sleeping for 5 minutes...${NC}"
    sleep 300
done
