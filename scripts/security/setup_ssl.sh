#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
DOMAIN="cg4f.online"
SUBDOMAINS=("api" "cdn")
EMAIL="admin@cg4f.online"
WEB_ROOT="/var/www/html"
NGINX_CONF_DIR="/etc/nginx/conf.d"
CERTBOT_DIR="/etc/letsencrypt/live"

# Function to log messages
log_message() {
    echo -e "${GREEN}$(date '+%Y-%m-%d %H:%M:%S'): $1${NC}"
}

# Function to log errors
log_error() {
    echo -e "${RED}$(date '+%Y-%m-%d %H:%M:%S'): $1${NC}" >&2
}

# Install required packages
install_dependencies() {
    log_message "Installing dependencies..."
    
    # Check if brew is installed
    if ! command -v brew &> /dev/null; then
        log_error "Homebrew is not installed. Please install it first."
        return 1
    }

    # Install certbot and nginx if not already installed
    brew list certbot &>/dev/null || brew install certbot
    brew list nginx &>/dev/null || brew install nginx
}

# Configure Nginx for SSL
setup_nginx() {
    log_message "Configuring Nginx..."
    
    # Create Nginx configuration
    cat > "${NGINX_CONF_DIR}/${DOMAIN}.conf" << EOF
# Security headers
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Content-Security-Policy "default-src 'self';" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;

# Main domain
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ${DOMAIN};

    ssl_certificate ${CERTBOT_DIR}/${DOMAIN}/fullchain.pem;
    ssl_certificate_key ${CERTBOT_DIR}/${DOMAIN}/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    # Modern configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 1.1.1.1 1.0.0.1 valid=300s;
    resolver_timeout 5s;

    root ${WEB_ROOT};
    index index.html;

    location / {
        try_files \$uri \$uri/ =404;
    }
}

# HTTP redirect
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN} *.${DOMAIN};
    return 301 https://\$host\$request_uri;
}
EOF

    # Test Nginx configuration
    nginx -t || {
        log_error "Nginx configuration test failed"
        return 1
    }

    # Reload Nginx
    nginx -s reload
}

# Get SSL certificate
get_ssl_certificate() {
    log_message "Getting SSL certificate..."
    
    # Build domain list for certbot
    DOMAIN_LIST="-d ${DOMAIN}"
    for subdomain in "${SUBDOMAINS[@]}"; do
        DOMAIN_LIST="${DOMAIN_LIST} -d ${subdomain}.${DOMAIN}"
    done

    # Get certificate
    certbot certonly \
        --nginx \
        --non-interactive \
        --agree-tos \
        --email "${EMAIL}" \
        ${DOMAIN_LIST} || {
        log_error "Failed to get SSL certificate"
        return 1
    }
}

# Set up auto-renewal
setup_auto_renewal() {
    log_message "Setting up auto-renewal..."
    
    # Create renewal script
    cat > /usr/local/bin/renew-certs.sh << EOF
#!/bin/bash
certbot renew --quiet --no-self-upgrade
nginx -s reload
EOF

    # Make it executable
    chmod +x /usr/local/bin/renew-certs.sh

    # Add to crontab (runs twice daily)
    (crontab -l 2>/dev/null; echo "0 0,12 * * * /usr/local/bin/renew-certs.sh") | crontab -
}

# Main execution
main() {
    log_message "Starting SSL setup..."

    # Run setup steps
    install_dependencies || exit 1
    setup_nginx || exit 1
    get_ssl_certificate || exit 1
    setup_auto_renewal || exit 1

    log_message "SSL setup completed successfully!"
    
    # Output next steps
    cat << EOF

SSL Setup Complete!

Your domain ${DOMAIN} is now configured with:
1. SSL certificates from Let's Encrypt
2. Automatic renewal (twice daily checks)
3. Modern SSL configuration
4. Security headers

To verify the setup:
1. Check SSL: https://www.ssllabs.com/ssltest/analyze.html?d=${DOMAIN}
2. Check Security Headers: https://securityheaders.com/?q=${DOMAIN}
3. Test HTTPS: curl -I https://${DOMAIN}

The certificates will be renewed automatically.
Manual renewal can be triggered with: certbot renew
EOF
}

# Run main function
main
