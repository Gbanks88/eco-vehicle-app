#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Base directories
BASE_DIR="/Volumes/Learn_Space/eco_vehicle_project/web"
BACKUP_DIR="$BASE_DIR/backups"
CONFIG_DIR="$BASE_DIR/config-backups"
LOG_DIR="$BASE_DIR/logs"

# Create necessary directories
mkdir -p "$BACKUP_DIR/daily"
mkdir -p "$BACKUP_DIR/weekly"
mkdir -p "$BACKUP_DIR/monthly"
mkdir -p "$CONFIG_DIR"

# Backup configuration files
backup_configs() {
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local config_backup="$CONFIG_DIR/config-$timestamp.tar.gz"
    
    echo -e "${BLUE}Backing up configuration files...${NC}"
    
    # Create tar archive of config files
    tar -czf "$config_backup" \
        -C "$BASE_DIR" \
        netlify.toml \
        public/_headers \
        public/_redirects \
        scripts/monitor-config.json \
        .env \
        next.config.js \
        package.json
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Configuration backup created: $config_backup${NC}"
    else
        echo -e "${RED}Failed to create configuration backup${NC}"
    fi
}

# Backup DNS records
backup_dns() {
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local dns_backup="$CONFIG_DIR/dns-$timestamp.txt"
    
    echo -e "${BLUE}Backing up DNS records...${NC}"
    
    # Get DNS records for all domains
    {
        echo "DNS Backup - $(date)"
        echo "===================="
        
        while IFS= read -r domain; do
            echo -e "\nDomain: $domain"
            echo "--------------------"
            dig +noall +answer "$domain" A
            dig +noall +answer "$domain" AAAA
            dig +noall +answer "$domain" CNAME
            dig +noall +answer "$domain" MX
            dig +noall +answer "$domain" TXT
            dig +noall +answer "$domain" NS
        done < <(jq -r '.domains | keys[]' "$BASE_DIR/scripts/monitor-config.json")
    } > "$dns_backup"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}DNS backup created: $dns_backup${NC}"
    else
        echo -e "${RED}Failed to create DNS backup${NC}"
    fi
}

# Backup logs
backup_logs() {
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local log_backup="$BACKUP_DIR/daily/logs-$timestamp.tar.gz"
    
    echo -e "${BLUE}Backing up logs...${NC}"
    
    # Create tar archive of logs
    tar -czf "$log_backup" -C "$BASE_DIR" logs/
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Log backup created: $log_backup${NC}"
    else
        echo -e "${RED}Failed to create log backup${NC}"
    fi
}

# Backup metrics
backup_metrics() {
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local metrics_backup="$BACKUP_DIR/daily/metrics-$timestamp.tar.gz"
    
    echo -e "${BLUE}Backing up metrics...${NC}"
    
    # Create tar archive of metrics
    tar -czf "$metrics_backup" -C "$BASE_DIR/logs" metrics/
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Metrics backup created: $metrics_backup${NC}"
    else
        echo -e "${RED}Failed to create metrics backup${NC}"
    fi
}

# Clean up old backups
cleanup_backups() {
    echo -e "${BLUE}Cleaning up old backups...${NC}"
    
    # Remove daily backups older than 7 days
    find "$BACKUP_DIR/daily" -type f -mtime +7 -delete
    
    # Remove weekly backups older than 30 days
    find "$BACKUP_DIR/weekly" -type f -mtime +30 -delete
    
    # Remove monthly backups older than 365 days
    find "$BACKUP_DIR/monthly" -type f -mtime +365 -delete
    
    # Remove config backups older than 30 days
    find "$CONFIG_DIR" -type f -mtime +30 -delete
    
    echo -e "${GREEN}Backup cleanup completed${NC}"
}

# Create full backup
create_full_backup() {
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local backup_type=$1
    local backup_file="$BACKUP_DIR/$backup_type/full-$timestamp.tar.gz"
    
    echo -e "${BLUE}Creating full $backup_type backup...${NC}"
    
    # Create tar archive of entire project
    tar --exclude='node_modules' \
        --exclude='.next' \
        --exclude='backups' \
        -czf "$backup_file" \
        -C "$BASE_DIR" .
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Full backup created: $backup_file${NC}"
    else
        echo -e "${RED}Failed to create full backup${NC}"
    fi
}

# Main backup process
case "$1" in
    daily)
        echo -e "${YELLOW}Starting daily backup...${NC}"
        backup_configs
        backup_dns
        backup_logs
        backup_metrics
        create_full_backup "daily"
        cleanup_backups
        ;;
    weekly)
        echo -e "${YELLOW}Starting weekly backup...${NC}"
        create_full_backup "weekly"
        cleanup_backups
        ;;
    monthly)
        echo -e "${YELLOW}Starting monthly backup...${NC}"
        create_full_backup "monthly"
        cleanup_backups
        ;;
    config)
        backup_configs
        ;;
    dns)
        backup_dns
        ;;
    logs)
        backup_logs
        ;;
    metrics)
        backup_metrics
        ;;
    cleanup)
        cleanup_backups
        ;;
    *)
        echo "Usage: $0 {daily|weekly|monthly|config|dns|logs|metrics|cleanup}"
        exit 1
        ;;
esac

exit 0
