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
REPORT_DIR="$BASE_DIR/reports"

# Create report directory
mkdir -p "$REPORT_DIR"

# Generate report filename
REPORT_FILE="$REPORT_DIR/security_report_$(date +%Y%m%d).md"

# Start report
cat << EOF > "$REPORT_FILE"
# Security Analysis Report
Generated: $(date '+%Y-%m-%d %H:%M:%S')

## Overview
This report provides a comprehensive security analysis of all domains and subdomains.

## Domain Security Status
EOF

# Function to analyze security headers
analyze_security_headers() {
    local domain=$1
    local headers
    headers=$(curl -sI "https://$domain")
    
    local score=100
    local issues=()
    
    # Check security headers
    if ! echo "$headers" | grep -q "Strict-Transport-Security"; then
        score=$((score - 20))
        issues+=("Missing HSTS header")
    fi
    if ! echo "$headers" | grep -q "Content-Security-Policy"; then
        score=$((score - 20))
        issues+=("Missing CSP header")
    fi
    if ! echo "$headers" | grep -q "X-Frame-Options"; then
        score=$((score - 15))
        issues+=("Missing X-Frame-Options header")
    fi
    if ! echo "$headers" | grep -q "X-Content-Type-Options"; then
        score=$((score - 15))
        issues+=("Missing X-Content-Type-Options header")
    fi
    
    echo "Security Score: $score"
    if [ ${#issues[@]} -gt 0 ]; then
        printf '%s\n' "${issues[@]}"
    fi
}

# Function to check SSL configuration
analyze_ssl() {
    local domain=$1
    local ssl_info
    
    ssl_info=$(openssl s_client -connect "$domain":443 -servername "$domain" 2>/dev/null)
    
    # Check TLS version
    local tls_version=$(echo "$ssl_info" | openssl x509 -noout -text | grep "TLS")
    
    # Check certificate expiry
    local expiry_date=$(echo "$ssl_info" | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
    local days_remaining=0
    if [ ! -z "$expiry_date" ]; then
        days_remaining=$(( ($(date -j -f "%b %d %H:%M:%S %Y %Z" "$expiry_date" +%s) - $(date +%s)) / 86400 ))
    fi
    
    echo "TLS Version: $tls_version"
    echo "Days until expiry: $days_remaining"
}

# Function to analyze DNS security
analyze_dns() {
    local domain=$1
    
    # Check DNSSEC
    local dnssec=$(dig +dnssec "$domain" | grep -c "RRSIG")
    
    # Check CAA records
    local caa=$(dig caa "$domain" +short)
    
    # Check SPF record
    local spf=$(dig txt "$domain" +short | grep "v=spf1")
    
    # Check DMARC record
    local dmarc=$(dig txt "_dmarc.$domain" +short)
    
    echo "DNSSEC: $([ $dnssec -gt 0 ] && echo "Enabled" || echo "Disabled")"
    echo "CAA: $([ -n "$caa" ] && echo "Configured" || echo "Not configured")"
    echo "SPF: $([ -n "$spf" ] && echo "Configured" || echo "Not configured")"
    echo "DMARC: $([ -n "$dmarc" ] && echo "Configured" || echo "Not configured")"
}

# Process each domain
while IFS= read -r domain; do
    echo -e "\n### $domain" >> "$REPORT_FILE"
    echo -e "\n#### Security Headers" >> "$REPORT_FILE"
    analyze_security_headers "$domain" >> "$REPORT_FILE"
    
    echo -e "\n#### SSL/TLS Configuration" >> "$REPORT_FILE"
    analyze_ssl "$domain" >> "$REPORT_FILE"
    
    echo -e "\n#### DNS Security" >> "$REPORT_FILE"
    analyze_dns "$domain" >> "$REPORT_FILE"
    
    # Add performance metrics if available
    if [ -f "$LOG_DIR/metrics/${domain//\//_}_$(date +%Y%m%d).csv" ]; then
        echo -e "\n#### Performance Metrics" >> "$REPORT_FILE"
        tail -n 1 "$LOG_DIR/metrics/${domain//\//_}_$(date +%Y%m%d).csv" >> "$REPORT_FILE"
    fi
done < <(jq -r '.domains | keys[]' "$BASE_DIR/scripts/monitor-config.json")

# Add recommendations section
cat << EOF >> "$REPORT_FILE"

## Security Recommendations

1. **SSL/TLS**
   - Ensure all certificates have at least 30 days before expiry
   - Use only TLS 1.2 or higher
   - Implement HSTS preloading

2. **Headers**
   - Implement all recommended security headers
   - Regular review and updates of CSP policies
   - Enable Feature-Policy headers for additional security

3. **DNS Security**
   - Enable DNSSEC for all domains
   - Implement CAA records
   - Configure SPF and DMARC records

4. **Monitoring**
   - Continue regular security scans
   - Monitor for unusual traffic patterns
   - Keep security configurations up to date

## Next Steps
1. Address any "High" priority issues immediately
2. Schedule reviews for "Medium" priority issues
3. Plan implementation of recommended security measures
4. Update monitoring configuration as needed

EOF

echo -e "${GREEN}Security report generated: $REPORT_FILE${NC}"
