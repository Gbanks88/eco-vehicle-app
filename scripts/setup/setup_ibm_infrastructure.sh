#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
DOMAIN="cg4f.online"
RESOURCE_GROUP="default"
REGION="us-south"
CIS_INSTANCE="cg4f-cis"
DNS_INSTANCE="cg4f-dns"
PRIMARY_IP="57.128.180.184"
LOG_FILE="$(pwd)/logs/setup.log"

# Function to log messages
log_message() {
    echo -e "${GREEN}$(date '+%Y-%m-%d %H:%M:%S'): $1${NC}" | tee -a "$LOG_FILE"
}

# Function to log errors
log_error() {
    echo -e "${RED}$(date '+%Y-%m-%d %H:%M:%S'): $1${NC}" | tee -a "$LOG_FILE" >&2
}

# Create DNS instance
create_dns_instance() {
    log_message "Creating DNS instance..."
    
    ibmcloud resource service-instance-create "$DNS_INSTANCE" \
        dns-svcs free "$REGION" || {
        log_error "Failed to create DNS instance"
        return 1
    }

    log_message "DNS instance created successfully"
}

# Create DNS zone
create_dns_zone() {
    log_message "Creating DNS zone..."
    
    ibmcloud dns zone-create "$DOMAIN" || {
        log_error "Failed to create DNS zone"
        return 1
    }

    log_message "DNS zone created successfully"
}

# Add DNS records
add_dns_records() {
    log_message "Adding DNS records..."
    
    # Add A record for root domain
    ibmcloud dns record-create "$DOMAIN" \
        --type=A --name="@" \
        --content="$PRIMARY_IP" --ttl=1800 || {
        log_error "Failed to create root A record"
        return 1
    }

    # Add A record for API subdomain
    ibmcloud dns record-create "$DOMAIN" \
        --type=A --name="api" \
        --content="$PRIMARY_IP" --ttl=3600 || {
        log_error "Failed to create API A record"
        return 1
    }

    # Add CNAME record for CDN
    ibmcloud dns record-create "$DOMAIN" \
        --type=CNAME --name="cdn" \
        --content="cg4l.site" --ttl=1800 || {
        log_error "Failed to create CDN CNAME record"
        return 1
    }

    log_message "DNS records added successfully"
}

# Create CIS instance
create_cis_instance() {
    log_message "Creating CIS instance..."
    
    ibmcloud resource service-instance-create "$CIS_INSTANCE" \
        internet-svcs standard "$REGION" || {
        log_error "Failed to create CIS instance"
        return 1
    }

    log_message "CIS instance created successfully"
}

# Configure SSL
configure_ssl() {
    log_message "Configuring SSL..."
    
    # Enable Universal SSL
    ibmcloud cis ssl-enable "$DOMAIN" || {
        log_error "Failed to enable SSL"
        return 1
    }

    # Set minimum TLS version
    ibmcloud cis tls-settings-update "$DOMAIN" \
        --min-tls-version=1.2 || {
        log_error "Failed to update TLS settings"
        return 1
    }

    # Enable HSTS
    ibmcloud cis security-level-update "$DOMAIN" high || {
        log_error "Failed to update security level"
        return 1
    }

    log_message "SSL configured successfully"
}

# Configure security
configure_security() {
    log_message "Configuring security settings..."
    
    # Enable WAF
    ibmcloud cis waf-update "$DOMAIN" --mode=on || {
        log_error "Failed to enable WAF"
        return 1
    }

    # Configure rate limiting
    ibmcloud cis rate-limit-create "$DOMAIN" \
        --threshold=100 \
        --period=60 \
        --match-request='{"url":"api.cg4f.online/*"}' || {
        log_error "Failed to configure rate limiting"
        return 1
    }

    log_message "Security configured successfully"
}

# Configure monitoring
configure_monitoring() {
    log_message "Setting up monitoring..."
    
    # Create health check for main domain
    ibmcloud cis health-check-create "$DOMAIN" \
        --name="Main Website" \
        --path="/" \
        --type=HTTP \
        --port=443 \
        --interval=60 || {
        log_error "Failed to create health check for main domain"
        return 1
    }

    # Create health check for API
    ibmcloud cis health-check-create "$DOMAIN" \
        --name="API Endpoint" \
        --path="/health" \
        --type=HTTPS \
        --port=443 \
        --interval=30 || {
        log_error "Failed to create health check for API"
        return 1
    }

    log_message "Monitoring configured successfully"
}

# Verify setup
verify_setup() {
    log_message "Verifying setup..."
    
    # Check DNS resolution
    dig @ns1.ibm.cloud "$DOMAIN" || {
        log_error "DNS resolution failed"
        return 1
    }

    # Wait for SSL provisioning
    log_message "Waiting for SSL certificate provisioning (may take up to 15 minutes)..."
    sleep 300  # Wait 5 minutes before first check

    # Check SSL certificate
    curl -vI "https://$DOMAIN" 2>&1 | grep "SSL certificate" || {
        log_error "SSL certificate verification failed"
        return 1
    }

    log_message "Setup verification completed"
}

# Main execution
main() {
    log_message "Starting IBM Cloud infrastructure setup..."

    # Target resource group
    log_message "Targeting resource group: $RESOURCE_GROUP"
    ibmcloud target -g "$RESOURCE_GROUP" || {
        log_error "Failed to target resource group"
        return 1
    }

    # Create instances
    create_dns_instance || exit 1
    create_cis_instance || exit 1

    # Configure DNS
    create_dns_zone || exit 1
    add_dns_records || exit 1

    # Configure SSL and security
    configure_ssl || exit 1
    configure_security || exit 1

    # Set up monitoring
    configure_monitoring || exit 1

    # Verify setup
    verify_setup || exit 1

    log_message "IBM Cloud infrastructure setup completed successfully"
    
    # Output next steps
    cat << EOF

Next Steps:
1. Update your domain registrar's nameservers to:
   - ns1.ibm.cloud
   - ns2.ibm.cloud

2. Wait for DNS propagation (up to 48 hours)

3. Verify the setup using:
   dig +trace $DOMAIN
   curl -vI https://$DOMAIN

4. Monitor the health checks at:
   https://cloud.ibm.com/internet-services/instances
EOF
}

# Create log directory
mkdir -p "$(dirname "$LOG_FILE")"

# Run main function
main
