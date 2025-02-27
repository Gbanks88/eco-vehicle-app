#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Load current credentials
source config/credentials.env

# Configuration
REMOTE_CONFIG_DIR="/opt/eco_vehicle/config"
DEPLOY_LOG="config/deploy.log"

# Function to log messages
log_message() {
    local level=$1
    local message=$2
    local color=$GREEN
    
    case $level in
        "WARNING") color=$YELLOW ;;
        "ERROR") color=$RED ;;
    esac
    
    echo -e "${color}$(date '+%Y-%m-%d %H:%M:%S') [$level] $message${NC}" | tee -a "$DEPLOY_LOG"
}

# Function to verify server connection
verify_connection() {
    ssh -p "$REMOTE_PORT" "$REMOTE_USER@$REMOTE_HOST" "echo 'Connection test'" &>/dev/null
    if [ $? -ne 0 ]; then
        log_message "ERROR" "Cannot connect to server $REMOTE_HOST"
        return 1
    fi
    log_message "INFO" "Successfully connected to server"
}

# Function to create remote directory structure
create_remote_dirs() {
    ssh -p "$REMOTE_PORT" "$REMOTE_USER@$REMOTE_HOST" "sudo mkdir -p $REMOTE_CONFIG_DIR && sudo chown $REMOTE_USER:$REMOTE_USER $REMOTE_CONFIG_DIR"
    if [ $? -ne 0 ]; then
        log_message "ERROR" "Failed to create remote directories"
        return 1
    fi
    log_message "INFO" "Created remote directories"
}

# Function to deploy credentials
deploy_credentials() {
    # First, encrypt credentials for transfer
    local temp_archive="config/credentials_deploy.tar.gz"
    tar czf "$temp_archive" -C config credentials.env.enc credentials.key
    
    # Deploy to server
    scp -P "$REMOTE_PORT" "$temp_archive" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_CONFIG_DIR/"
    if [ $? -ne 0 ]; then
        log_message "ERROR" "Failed to copy credentials to server"
        rm "$temp_archive"
        return 1
    fi
    
    # Extract and set up on server
    ssh -p "$REMOTE_PORT" "$REMOTE_USER@$REMOTE_HOST" "cd $REMOTE_CONFIG_DIR && \
        tar xzf credentials_deploy.tar.gz && \
        rm credentials_deploy.tar.gz && \
        chmod 600 credentials.env.enc credentials.key"
    
    if [ $? -ne 0 ]; then
        log_message "ERROR" "Failed to set up credentials on server"
        rm "$temp_archive"
        return 1
    fi
    
    # Clean up local temp file
    rm "$temp_archive"
    
    log_message "INFO" "Successfully deployed credentials to server"
}

# Function to verify deployment
verify_deployment() {
    # Try to decrypt credentials on server
    ssh -p "$REMOTE_PORT" "$REMOTE_USER@$REMOTE_HOST" "cd $REMOTE_CONFIG_DIR && \
        openssl enc -d -aes-256-cbc -in credentials.env.enc -out credentials.env -pass file:credentials.key && \
        test -f credentials.env && \
        grep -q 'REMOTE_HOST' credentials.env && \
        rm credentials.env"
    
    if [ $? -ne 0 ]; then
        log_message "ERROR" "Failed to verify credentials on server"
        return 1
    fi
    
    log_message "INFO" "Verified credentials deployment"
}

# Function to show deployment history
show_deploy_history() {
    if [ -f "$DEPLOY_LOG" ]; then
        echo "=== Credential Deployment History ==="
        cat "$DEPLOY_LOG"
    else
        echo "No deployment history found"
    fi
}

# Main deployment process
main() {
    log_message "INFO" "Starting credential deployment to $REMOTE_HOST"
    
    verify_connection || exit 1
    create_remote_dirs || exit 1
    deploy_credentials || exit 1
    verify_deployment || exit 1
    
    log_message "INFO" "Credential deployment completed successfully"
}

# Function to show usage
show_usage() {
    echo "Usage:"
    echo "  $0 deploy                           # Deploy credentials to server"
    echo "  $0 history                          # Show deployment history"
}

# Parse command line arguments
case "$1" in
    "deploy")
        main
        ;;
    "history")
        show_deploy_history
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
