#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
DOMAIN="cg4f.online"
CERT_DIR="/etc/cg4f/ssl"
LOG_FILE="/var/log/cg4f/ssl_recovery.log"
EMAIL="admin@cg4f.online"

# Function to log messages
log_message() {
    echo -e "${GREEN}$(date '+%Y-%m-%d %H:%M:%S'): $1${NC}" | tee -a "$LOG_FILE"
}

# Function to log errors
log_error() {
    echo -e "${RED}$(date '+%Y-%m-%d %H:%M:%S'): $1${NC}" | tee -a "$LOG_FILE" >&2
}

# Install certbot if not present
install_certbot() {
    log_message "Checking certbot installation..."
    
    if ! command -v certbot &> /dev/null; then
        log_message "Installing certbot..."
        brew install certbot || {
            log_error "Failed to install certbot"
            return 1
        }
    fi
}

# Generate emergency certificates
generate_certificates() {
    log_message "Generating emergency certificates..."
    
    # Create certificate directory
    mkdir -p "$CERT_DIR"

    # Generate certificates using Let's Encrypt
    certbot certonly --standalone \
        -d "$DOMAIN" \
        -d "api.$DOMAIN" \
        -d "cdn.$DOMAIN" \
        --email "$EMAIL" \
        --agree-tos \
        --non-interactive \
        --cert-dir "$CERT_DIR" || {
        log_error "Failed to generate certificates"
        return 1
    }

    log_message "Certificates generated successfully"
}

# Verify certificates
verify_certificates() {
    log_message "Verifying certificates..."
    
    # Check certificate validity
    openssl x509 -in "$CERT_DIR/live/$DOMAIN/cert.pem" -noout -text | grep "Not After" || {
        log_error "Certificate verification failed"
        return 1
    }

    # Check certificate chain
    openssl verify -CAfile "$CERT_DIR/live/$DOMAIN/chain.pem" "$CERT_DIR/live/$DOMAIN/cert.pem" || {
        log_error "Certificate chain verification failed"
        return 1
    }

    log_message "Certificate verification successful"
}

# Update IBM CIS
update_cis() {
    log_message "Updating IBM CIS with new certificates..."
    
    # Upload certificate to IBM CIS
    ibmcloud cis certificate-upload "$DOMAIN" \
        --certificate-file "$CERT_DIR/live/$DOMAIN/cert.pem" \
        --private-key-file "$CERT_DIR/live/$DOMAIN/privkey.pem" \
        --bundle-method ubiquitous || {
        log_error "Failed to upload certificate to IBM CIS"
        return 1
    }

    log_message "IBM CIS updated successfully"
}

# Update monitoring
update_monitoring() {
    log_message "Updating monitoring configuration..."
    
    # Update SSL certificate paths in monitoring config
    sed -i.bak "s|ssl_certificate_path:.*|ssl_certificate_path: $CERT_DIR/live/$DOMAIN/cert.pem|g" \
        /etc/cg4f/monitoring/ssl_config.yml

    # Restart monitoring service
    systemctl restart cg4f-monitoring || {
        log_error "Failed to restart monitoring service"
        return 1
    }

    log_message "Monitoring updated successfully"
}

# Notify team
notify_team() {
    log_message "Notifying team of SSL certificate update..."
    
    # Send Slack notification
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"Emergency SSL certificates generated and deployed for $DOMAIN\"}" \
        "$SLACK_WEBHOOK_URL"

    # Send email notification
    echo "Emergency SSL certificates have been generated and deployed for $DOMAIN" | \
        mail -s "SSL Certificate Update" devops-team@cg4f.online

    log_message "Team notifications sent"
}

# Main execution
main() {
    log_message "Starting emergency SSL certificate generation..."

    # Install certbot
    install_certbot || exit 1

    # Generate certificates
    generate_certificates || exit 1

    # Verify certificates
    verify_certificates || exit 1

    # Update IBM CIS
    update_cis || exit 1

    # Update monitoring
    update_monitoring || exit 1

    # Notify team
    notify_team

    log_message "Emergency SSL certificate generation completed successfully"
}

# Run main function
main
