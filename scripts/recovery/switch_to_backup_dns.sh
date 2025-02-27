#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
DOMAIN="cg4f.online"
BACKUP_NS1="backup-ns1.cloudflare.com"
BACKUP_NS2="backup-ns2.cloudflare.com"
PRIMARY_IP="57.128.180.184"
LOG_FILE="/var/log/cg4f/dns_recovery.log"

# Function to log messages
log_message() {
    echo -e "${GREEN}$(date '+%Y-%m-%d %H:%M:%S'): $1${NC}" | tee -a "$LOG_FILE"
}

# Function to log errors
log_error() {
    echo -e "${RED}$(date '+%Y-%m-%d %H:%M:%S'): $1${NC}" | tee -a "$LOG_FILE" >&2
}

# Create backup DNS zone in Cloudflare
create_backup_zone() {
    log_message "Creating backup DNS zone in Cloudflare..."
    
    # Create zone
    cloudflare zone create --zone="$DOMAIN" --jump-start=false || {
        log_error "Failed to create backup zone"
        return 1
    }

    # Add DNS records
    cloudflare dns add --zone="$DOMAIN" --type=A --name="@" --content="$PRIMARY_IP" --ttl=300 || {
        log_error "Failed to add root A record"
        return 1
    }

    cloudflare dns add --zone="$DOMAIN" --type=A --name="api" --content="$PRIMARY_IP" --ttl=300 || {
        log_error "Failed to add API A record"
        return 1
    }

    cloudflare dns add --zone="$DOMAIN" --type=CNAME --name="cdn" --content="cg4l.site" --ttl=300 || {
        log_error "Failed to add CDN CNAME record"
        return 1
    }

    log_message "Backup zone created successfully"
}

# Verify DNS propagation
verify_dns() {
    log_message "Verifying DNS propagation..."
    
    # Check main domain
    dig @"$BACKUP_NS1" "$DOMAIN" +short | grep -q "$PRIMARY_IP" || {
        log_error "Main domain not resolving correctly"
        return 1
    }

    # Check API subdomain
    dig @"$BACKUP_NS1" "api.$DOMAIN" +short | grep -q "$PRIMARY_IP" || {
        log_error "API subdomain not resolving correctly"
        return 1
    }

    # Check CDN subdomain
    dig @"$BACKUP_NS1" "cdn.$DOMAIN" +short | grep -q "cg4l.site" || {
        log_error "CDN subdomain not resolving correctly"
        return 1
    }

    log_message "DNS verification successful"
}

# Update monitoring
update_monitoring() {
    log_message "Updating monitoring configuration..."
    
    # Update nameserver configuration in monitoring
    sed -i.bak "s/ns1.ibm.cloud/$BACKUP_NS1/g" /etc/cg4f/monitoring/dns_config.yml
    sed -i.bak "s/ns2.ibm.cloud/$BACKUP_NS2/g" /etc/cg4f/monitoring/dns_config.yml

    # Restart monitoring service
    systemctl restart cg4f-monitoring || {
        log_error "Failed to restart monitoring service"
        return 1
    }

    log_message "Monitoring updated successfully"
}

# Notify team
notify_team() {
    log_message "Notifying team of DNS switchover..."
    
    # Send Slack notification
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"DNS Failover: Switched to backup DNS for $DOMAIN\"}" \
        "$SLACK_WEBHOOK_URL"

    # Send email notification
    echo "DNS Failover: Switched to backup DNS for $DOMAIN" | \
        mail -s "DNS Failover Alert" devops-team@cg4f.online

    log_message "Team notifications sent"
}

# Main execution
main() {
    log_message "Starting DNS failover process..."

    # Create backup zone
    create_backup_zone || exit 1

    # Wait for DNS propagation
    log_message "Waiting for DNS propagation (300 seconds)..."
    sleep 300

    # Verify DNS
    verify_dns || exit 1

    # Update monitoring
    update_monitoring || exit 1

    # Notify team
    notify_team

    log_message "DNS failover completed successfully"
}

# Run main function
main
