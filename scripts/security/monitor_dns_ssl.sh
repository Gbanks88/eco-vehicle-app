#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
DOMAIN="cg4f.online"
SUBDOMAINS=("api" "cdn")
LOG_FILE="/var/log/dns_monitor.log"
ALERT_EMAIL="admin@cg4f.online"

# Function to log messages
log_message() {
    local level=$1
    local message=$2
    local color=$GREEN
    
    case $level in
        "WARNING") color=$YELLOW ;;
        "ERROR") color=$RED ;;
    esac
    
    echo -e "${color}$(date '+%Y-%m-%d %H:%M:%S') [$level] $message${NC}" | tee -a "$LOG_FILE"
}

# Check DNS records
check_dns() {
    log_message "INFO" "Checking DNS records..."
    
    # Check A record
    local main_ip=$(dig +short "$DOMAIN")
    if [ -z "$main_ip" ]; then
        log_message "ERROR" "Main domain A record not found"
        return 1
    fi
    
    # Check subdomains
    for subdomain in "${SUBDOMAINS[@]}"; do
        local sub_ip=$(dig +short "${subdomain}.${DOMAIN}")
        if [ -z "$sub_ip" ]; then
            log_message "ERROR" "Subdomain ${subdomain} record not found"
            return 1
        fi
    done
    
    # Check security records
    local spf=$(dig +short TXT "$DOMAIN" | grep "v=spf1")
    local dmarc=$(dig +short TXT "_dmarc.${DOMAIN}")
    local caa=$(dig +short CAA "$DOMAIN")
    
    [ -z "$spf" ] && log_message "WARNING" "SPF record missing"
    [ -z "$dmarc" ] && log_message "WARNING" "DMARC record missing"
    [ -z "$caa" ] && log_message "WARNING" "CAA record missing"
}

# Check SSL certificate
check_ssl() {
    log_message "INFO" "Checking SSL certificate..."
    
    # Check main domain SSL
    local ssl_info=$(echo | openssl s_client -connect "${DOMAIN}:443" 2>/dev/null)
    if [ $? -ne 0 ]; then
        log_message "ERROR" "SSL connection failed for ${DOMAIN}"
        return 1
    fi
    
    # Check certificate expiration
    local expiry_date=$(echo "$ssl_info" | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
    local expiry_epoch=$(date -j -f "%b %d %H:%M:%S %Y %Z" "$expiry_date" +%s)
    local current_epoch=$(date +%s)
    local days_left=$(( ($expiry_epoch - $current_epoch) / 86400 ))
    
    if [ $days_left -lt 30 ]; then
        log_message "WARNING" "SSL certificate expires in $days_left days"
    else
        log_message "INFO" "SSL certificate valid for $days_left days"
    fi
}

# Check security headers
check_security_headers() {
    log_message "INFO" "Checking security headers..."
    
    local headers=$(curl -sI "https://${DOMAIN}")
    
    # Check required headers
    local required_headers=(
        "Strict-Transport-Security"
        "X-Frame-Options"
        "X-Content-Type-Options"
        "Content-Security-Policy"
    )
    
    for header in "${required_headers[@]}"; do
        if ! echo "$headers" | grep -q "$header"; then
            log_message "WARNING" "Missing security header: $header"
        fi
    done
}

# Send alert if issues found
send_alert() {
    local message=$1
    echo "$message" | mail -s "DNS/SSL Alert for ${DOMAIN}" "$ALERT_EMAIL"
}

# Main monitoring function
monitor() {
    local has_error=0
    
    # Create log directory if it doesn't exist
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Run checks
    check_dns || has_error=1
    check_ssl || has_error=1
    check_security_headers || has_error=1
    
    # If errors found, send alert
    if [ $has_error -eq 1 ]; then
        send_alert "$(tail -n 50 "$LOG_FILE")"
    fi
    
    # Output summary
    if [ $has_error -eq 0 ]; then
        log_message "INFO" "All checks passed successfully"
    else
        log_message "ERROR" "Some checks failed - see log for details"
    fi
}

# Run monitoring
monitor
