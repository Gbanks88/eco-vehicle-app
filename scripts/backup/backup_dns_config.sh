#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
BACKUP_DIR="/Volumes/Learn_Space/eco_vehicle_project/backups/dns"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Function to log messages
log_message() {
    echo -e "${GREEN}$(date '+%Y-%m-%d %H:%M:%S'): $1${NC}"
}

# Function to log errors
log_error() {
    echo -e "${RED}$(date '+%Y-%m-%d %H:%M:%S'): $1${NC}" >&2
}

# Backup DNS records
backup_dns_records() {
    log_message "Starting DNS records backup..."
    
    # Backup DNS zone
    ibmcloud dns zone-export cg4f.online > "$BACKUP_DIR/zone_${DATE}.txt" || {
        log_error "Failed to export DNS zone"
        return 1
    }

    # Backup DNS records
    ibmcloud dns records cg4f.online > "$BACKUP_DIR/records_${DATE}.txt" || {
        log_error "Failed to export DNS records"
        return 1
    }

    # Backup CIS configuration
    ibmcloud cis instance-get cg4f-cis --output json > "$BACKUP_DIR/cis_config_${DATE}.json" || {
        log_error "Failed to export CIS configuration"
        return 1
    }

    # Create checksum files
    cd "$BACKUP_DIR" || exit 1
    sha256sum "zone_${DATE}.txt" "records_${DATE}.txt" "cis_config_${DATE}.json" > "checksum_${DATE}.txt"

    log_message "DNS backup completed successfully"
}

# Backup security configuration
backup_security_config() {
    log_message "Starting security configuration backup..."
    
    # Backup WAF rules
    ibmcloud cis waf-rules cg4f.online --output json > "$BACKUP_DIR/waf_rules_${DATE}.json" || {
        log_error "Failed to export WAF rules"
        return 1
    }

    # Backup Page Rules
    ibmcloud cis page-rules cg4f.online --output json > "$BACKUP_DIR/page_rules_${DATE}.json" || {
        log_error "Failed to export page rules"
        return 1
    }

    # Backup SSL configuration
    ibmcloud cis tls-settings cg4f.online --output json > "$BACKUP_DIR/ssl_config_${DATE}.json" || {
        log_error "Failed to export SSL configuration"
        return 1
    }

    log_message "Security configuration backup completed successfully"
}

# Clean up old backups
cleanup_old_backups() {
    log_message "Cleaning up old backups..."
    find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete
    log_message "Cleanup completed"
}

# Upload backup to IBM Cloud Storage
upload_to_cloud() {
    log_message "Uploading backup to cloud storage..."
    
    # Create tar archive
    tar -czf "$BACKUP_DIR/backup_${DATE}.tar.gz" -C "$BACKUP_DIR" .

    # Upload to IBM Cloud Storage
    ibmcloud cos upload --bucket cg4f-backups --key "dns_backup_${DATE}.tar.gz" --file "$BACKUP_DIR/backup_${DATE}.tar.gz" || {
        log_error "Failed to upload backup to cloud storage"
        return 1
    }

    log_message "Backup uploaded to cloud storage successfully"
}

# Main execution
main() {
    log_message "Starting backup process..."

    # Create backup directory for this run
    BACKUP_DIR="$BACKUP_DIR/$DATE"
    mkdir -p "$BACKUP_DIR"

    # Run backups
    backup_dns_records || exit 1
    backup_security_config || exit 1
    
    # Upload to cloud
    upload_to_cloud || exit 1
    
    # Cleanup
    cleanup_old_backups

    log_message "Backup process completed successfully"
}

# Run main function
main
