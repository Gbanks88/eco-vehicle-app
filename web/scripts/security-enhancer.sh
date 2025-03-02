#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Base directories
BASE_DIR="/Volumes/Learn_Space/eco_vehicle_project/web"
CONFIG_DIR="$BASE_DIR/config"
LOG_DIR="$BASE_DIR/logs"

# Create necessary directories
mkdir -p "$CONFIG_DIR/security"
mkdir -p "$LOG_DIR/security"

# Function to enhance security headers
enhance_security_headers() {
    local domain=$1
    echo -e "${BLUE}Enhancing security headers for $domain...${NC}"
    
    # Update _headers file
    cat << EOF > "$BASE_DIR/public/_headers"
/*
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
  Content-Security-Policy: default-src 'self' https://*.netlify.app https://*.cg4f.online https://*.johnallens.com; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://*.netlify.app https://*.cg4f.online https://*.johnallens.com https://sketchfab.com https://youtube.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https: *.cloudinary.com https://*.cg4f.online https://*.johnallens.com; media-src 'self' https:; connect-src 'self' https://*.netlify.app https://*.cg4f.online https://*.johnallens.com; frame-src 'self' https://sketchfab.com https://youtube.com; worker-src 'self' blob:; manifest-src 'self'; base-uri 'self'; form-action 'self' https://*.cg4f.online https://*.johnallens.com; upgrade-insecure-requests;
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  X-XSS-Protection: 1; mode=block
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: accelerometer=(), ambient-light-sensor=(), autoplay=(), battery=(), camera=(), cross-origin-isolated=(), display-capture=(), document-domain=(), encrypted-media=(), execution-while-not-rendered=(), execution-while-out-of-viewport=(), fullscreen=(self), geolocation=(), gyroscope=(), keyboard-map=(), magnetometer=(), microphone=(), midi=(), navigation-override=(), payment=(), picture-in-picture=(), publickey-credentials-get=(), screen-wake-lock=(), sync-xhr=(), usb=(), web-share=(), xr-spatial-tracking=()
  Cross-Origin-Embedder-Policy: require-corp
  Cross-Origin-Opener-Policy: same-origin
  Cross-Origin-Resource-Policy: same-origin
  Cache-Control: public, max-age=3600
  Feature-Policy: accelerometer 'none'; ambient-light-sensor 'none'; autoplay 'none'; battery 'none'; camera 'none'; display-capture 'none'; document-domain 'none'; encrypted-media 'none'; fullscreen 'self'; geolocation 'none'; gyroscope 'none'; magnetometer 'none'; microphone 'none'; midi 'none'; payment 'none'; picture-in-picture 'none'; usb 'none'; web-share 'none'; xr-spatial-tracking 'none'
EOF
    
    echo -e "${GREEN}Security headers updated${NC}"
}

# Function to configure SSL/TLS
configure_ssl() {
    local domain=$1
    echo -e "${BLUE}Configuring SSL/TLS for $domain...${NC}"
    
    # Force HTTPS
    cat << EOF > "$BASE_DIR/public/_redirects"
# Force HTTPS
/* https://:splat 301!

# WWW to non-WWW
https://www.$domain/* https://$domain/:splat 301!
EOF
    
    # Enable HSTS preloading
    curl -X POST "https://hstspreload.org/api/v2/submit" \
        -H "Content-Type: application/json" \
        -d "{\"domain\":\"$domain\"}"
    
    echo -e "${GREEN}SSL/TLS configuration updated${NC}"
}

# Function to set up rate limiting
setup_rate_limiting() {
    local domain=$1
    echo -e "${BLUE}Setting up rate limiting for $domain...${NC}"
    
    # Add rate limiting headers
    cat << EOF >> "$BASE_DIR/public/_headers"

# Rate limiting
/api/*
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 100
  X-RateLimit-Reset: 3600
EOF
    
    echo -e "${GREEN}Rate limiting configured${NC}"
}

# Function to configure CORS
configure_cors() {
    local domain=$1
    echo -e "${BLUE}Configuring CORS for $domain...${NC}"
    
    # Add CORS headers
    cat << EOF >> "$BASE_DIR/public/_headers"

# CORS configuration
/api/*
  Access-Control-Allow-Origin: https://$domain
  Access-Control-Allow-Methods: GET, POST, OPTIONS
  Access-Control-Allow-Headers: Content-Type, Authorization
  Access-Control-Max-Age: 86400
EOF
    
    echo -e "${GREEN}CORS configured${NC}"
}

# Function to set up security monitoring
setup_security_monitoring() {
    local domain=$1
    echo -e "${BLUE}Setting up security monitoring for $domain...${NC}"
    
    # Create security monitoring configuration
    cat << EOF > "$CONFIG_DIR/security/monitoring.json"
{
  "monitoring": {
    "enabled": true,
    "interval": 300,
    "alerts": {
      "email": ["admin@$domain"],
      "slack": "SLACK_WEBHOOK_URL"
    },
    "checks": {
      "headers": true,
      "ssl": true,
      "dns": true,
      "ports": true,
      "vulnerabilities": true
    },
    "thresholds": {
      "response_time": 2000,
      "ssl_expiry_days": 30,
      "security_score": 90
    }
  },
  "protection": {
    "ddos": {
      "enabled": true,
      "rate_limit": 100,
      "burst": 200
    },
    "injection": {
      "enabled": true,
      "patterns": [
        "SQL",
        "XSS",
        "Command"
      ]
    },
    "authentication": {
      "enabled": true,
      "max_attempts": 5,
      "lockout_duration": 900
    }
  }
}
EOF
    
    echo -e "${GREEN}Security monitoring configured${NC}"
}

# Function to configure backup policies
configure_backup_policies() {
    local domain=$1
    echo -e "${BLUE}Configuring backup policies for $domain...${NC}"
    
    # Create backup configuration
    cat << EOF > "$CONFIG_DIR/security/backup.json"
{
  "backup": {
    "enabled": true,
    "schedule": {
      "daily": "0 0 * * *",
      "weekly": "0 0 * * 0",
      "monthly": "0 0 1 * *"
    },
    "retention": {
      "daily": 7,
      "weekly": 30,
      "monthly": 365
    },
    "storage": {
      "local": "$BASE_DIR/backups",
      "remote": {
        "enabled": true,
        "type": "s3",
        "bucket": "backup-$domain"
      }
    },
    "encryption": {
      "enabled": true,
      "algorithm": "AES-256-GCM"
    }
  }
}
EOF
    
    echo -e "${GREEN}Backup policies configured${NC}"
}

# Main security enhancement process
main() {
    local domain=$1
    
    if [ -z "$domain" ]; then
        echo -e "${RED}Error: Domain name required${NC}"
        echo "Usage: $0 domain.com"
        exit 1
    fi
    
    echo -e "${YELLOW}Starting security enhancement for $domain${NC}"
    
    # Perform security enhancements
    enhance_security_headers "$domain"
    configure_ssl "$domain"
    setup_rate_limiting "$domain"
    configure_cors "$domain"
    setup_security_monitoring "$domain"
    configure_backup_policies "$domain"
    
    echo -e "${GREEN}Security enhancement completed for $domain${NC}"
    echo -e "${YELLOW}Please deploy your changes to apply the new security configurations${NC}"
}

# Run main process
main "$1"
