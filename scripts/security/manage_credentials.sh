#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
CREDENTIALS_FILE="config/credentials.env"
ENCRYPTED_FILE="config/credentials.env.enc"
KEY_FILE="config/credentials.key"

# Function to generate a secure key
generate_key() {
    openssl rand -base64 32 > "$KEY_FILE"
    chmod 600 "$KEY_FILE"
    echo -e "${GREEN}Generated encryption key at $KEY_FILE${NC}"
}

# Function to encrypt credentials
encrypt_credentials() {
    if [ ! -f "$KEY_FILE" ]; then
        generate_key
    fi
    
    openssl enc -aes-256-cbc -salt -in "$CREDENTIALS_FILE" -out "$ENCRYPTED_FILE" -pass file:"$KEY_FILE"
    chmod 600 "$ENCRYPTED_FILE"
    echo -e "${GREEN}Encrypted credentials saved to $ENCRYPTED_FILE${NC}"
}

# Function to decrypt credentials
decrypt_credentials() {
    if [ ! -f "$KEY_FILE" ]; then
        echo -e "${RED}Error: Encryption key not found at $KEY_FILE${NC}"
        exit 1
    fi
    
    openssl enc -d -aes-256-cbc -in "$ENCRYPTED_FILE" -out "$CREDENTIALS_FILE" -pass file:"$KEY_FILE"
    chmod 600 "$CREDENTIALS_FILE"
    echo -e "${GREEN}Decrypted credentials saved to $CREDENTIALS_FILE${NC}"
}

# Function to update a credential
update_credential() {
    local key=$1
    local value=$2
    
    if [ ! -f "$CREDENTIALS_FILE" ]; then
        echo -e "${RED}Error: Credentials file not found${NC}"
        exit 1
    fi
    
    # Update or add the credential
    if grep -q "^$key=" "$CREDENTIALS_FILE"; then
        sed -i '' "s|^$key=.*|$key=$value|" "$CREDENTIALS_FILE"
    else
        echo "$key=$value" >> "$CREDENTIALS_FILE"
    fi
    
    echo -e "${GREEN}Updated credential: $key${NC}"
    
    # Re-encrypt the file
    encrypt_credentials
}

# Function to setup Forge credentials
setup_forge() {
    echo "Setting up Autodesk Forge credentials..."
    
    # Prompt for credentials
    read -p "Enter Forge Client ID: " forge_client_id
    read -p "Enter Forge Client Secret: " forge_client_secret
    read -p "Enter Forge Callback URL [$DOMAIN/callback/forge]: " forge_callback_url
    forge_callback_url=${forge_callback_url:-"https://$DOMAIN/callback/forge"}
    
    # Update credentials
    update_credential "FORGE_CLIENT_ID" "$forge_client_id"
    update_credential "FORGE_CLIENT_SECRET" "$forge_client_secret"
    update_credential "FORGE_CALLBACK_URL" "$forge_callback_url"
    update_credential "MODEL_DERIVATIVE_API_URL" "https://developer.api.autodesk.com/modelderivative/v2"
    update_credential "FORGE_BUCKET_KEY" "eco_vehicle_models"
    
    echo -e "${GREEN}Forge credentials setup complete${NC}"
    
    # Encrypt updated credentials
    encrypt_credentials
}

# Function to show usage
show_usage() {
    echo "Usage:"
    echo "  $0 encrypt                          # Encrypt credentials file"
    echo "  $0 decrypt                          # Decrypt credentials file"
    echo "  $0 update KEY VALUE                 # Update a specific credential"
    echo "  $0 generate-key                     # Generate new encryption key"
    echo "  $0 setup-forge                      # Setup Autodesk Forge credentials"
    echo ""
    echo "Example:"
    echo "  $0 update REMOTE_PASSWORD mypassword"
}

# Main execution
case "$1" in
    "encrypt")
        encrypt_credentials
        ;;
    "decrypt")
        decrypt_credentials
        ;;
    "update")
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo -e "${RED}Error: Both KEY and VALUE are required for update${NC}"
            show_usage
            exit 1
        fi
        update_credential "$2" "$3"
        ;;
    "generate-key")
        generate_key
        ;;
    "setup-forge")
        setup_forge
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
