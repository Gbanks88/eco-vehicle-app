#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
CREDENTIALS_DIR="config"
BACKUP_DIR="config/backups"
ROTATION_LOG="config/rotation.log"
MAX_BACKUPS=5

# Function to log messages
log_message() {
    local level=$1
    local message=$2
    local color=$GREEN
    
    case $level in
        "WARNING") color=$YELLOW ;;
        "ERROR") color=$RED ;;
    esac
    
    echo -e "${color}$(date '+%Y-%m-%d %H:%M:%S') [$level] $message${NC}" | tee -a "$ROTATION_LOG"
}

# Function to generate a secure password
generate_password() {
    openssl rand -base64 32 | tr -d '/+=' | cut -c1-20
}

# Function to backup current credentials
backup_credentials() {
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="${BACKUP_DIR}/credentials_${timestamp}.enc"
    
    mkdir -p "$BACKUP_DIR"
    cp "${CREDENTIALS_DIR}/credentials.env.enc" "$backup_file"
    cp "${CREDENTIALS_DIR}/credentials.key" "${backup_file}.key"
    
    # Keep only the last MAX_BACKUPS backups
    (cd "$BACKUP_DIR" && ls -t credentials_*.enc | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm)
    (cd "$BACKUP_DIR" && ls -t credentials_*.key | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm)
    
    log_message "INFO" "Backed up credentials to $backup_file"
}

# Function to rotate a specific credential
rotate_credential() {
    local key=$1
    local new_value=$2
    
    # Decrypt current credentials
    ./scripts/security/manage_credentials.sh decrypt
    
    if [ $? -ne 0 ]; then
        log_message "ERROR" "Failed to decrypt credentials"
        return 1
    fi
    
    # Update the credential
    ./scripts/security/manage_credentials.sh update "$key" "$new_value"
    
    if [ $? -ne 0 ]; then
        log_message "ERROR" "Failed to update credential: $key"
        return 1
    fi
    
    log_message "INFO" "Rotated credential: $key"
}

# Function to rotate all credentials
rotate_all_credentials() {
    log_message "INFO" "Starting credential rotation"
    
    # Backup current credentials
    backup_credentials
    
    # Generate new passwords
    local new_remote_password=$(generate_password)
    local new_api_key=$(generate_password)
    local new_db_password=$(generate_password)
    
    # Rotate each credential
    rotate_credential "REMOTE_PASSWORD" "$new_remote_password"
    rotate_credential "NAMECHEAP_API_KEY" "$new_api_key"
    rotate_credential "DB_PASSWORD" "$new_db_password"
    
    # Deploy new credentials to server
    ./scripts/security/deploy_credentials.sh
    
    if [ $? -eq 0 ]; then
        log_message "INFO" "Successfully rotated and deployed all credentials"
    else
        log_message "ERROR" "Failed to deploy new credentials"
        # Restore from backup
        local latest_backup=$(ls -t "${BACKUP_DIR}/credentials_"*.enc | head -1)
        if [ -n "$latest_backup" ]; then
            cp "$latest_backup" "${CREDENTIALS_DIR}/credentials.env.enc"
            cp "${latest_backup}.key" "${CREDENTIALS_DIR}/credentials.key"
            log_message "WARNING" "Restored credentials from backup"
        fi
    fi
}

# Function to show rotation history
show_rotation_history() {
    if [ -f "$ROTATION_LOG" ]; then
        echo "=== Credential Rotation History ==="
        cat "$ROTATION_LOG"
    else
        echo "No rotation history found"
    fi
}

# Function to show usage
show_usage() {
    echo "Usage:"
    echo "  $0 rotate-all                       # Rotate all credentials"
    echo "  $0 rotate KEY                       # Rotate specific credential"
    echo "  $0 history                          # Show rotation history"
    echo ""
    echo "Example:"
    echo "  $0 rotate REMOTE_PASSWORD"
}

# Main execution
case "$1" in
    "rotate-all")
        rotate_all_credentials
        ;;
    "rotate")
        if [ -z "$2" ]; then
            echo -e "${RED}Error: KEY is required for rotation${NC}"
            show_usage
            exit 1
        fi
        rotate_credential "$2" "$(generate_password)"
        ;;
    "history")
        show_rotation_history
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
