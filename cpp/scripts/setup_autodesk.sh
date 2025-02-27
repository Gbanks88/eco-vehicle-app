#!/bin/bash

# Exit on error
set -e

# Configuration
AUTODESK_VERSION="2025"
FUSION360_VERSION="2.0.16992"
INSTALL_DIR="$(pwd)/third_party"
TEMP_DIR="/tmp/autodesk_setup"

# Create directories
mkdir -p "$INSTALL_DIR"
mkdir -p "$TEMP_DIR"

echo "Setting up Autodesk development environment..."

# Download and install Autodesk Platform Services SDK
echo "Installing Autodesk Platform Services SDK..."
cd "$TEMP_DIR"

if [ ! -d "$INSTALL_DIR/aps_sdk" ]; then
    # Note: Replace with actual download URL when available
    curl -L "https://developer.autodesk.com/api/aps-sdk-cpp-$AUTODESK_VERSION.tar.gz" -o aps_sdk.tar.gz
    tar xzf aps_sdk.tar.gz
    mv aps_sdk "$INSTALL_DIR/"
    echo "export AUTODESK_SDK_ROOT=$INSTALL_DIR/aps_sdk" >> ~/.zshrc
fi

# Download and install Fusion 360 SDK
echo "Installing Fusion 360 SDK..."
if [ ! -d "$INSTALL_DIR/fusion360_sdk" ]; then
    # Note: Replace with actual download URL when available
    curl -L "https://developer.autodesk.com/api/fusion360-cpp-$FUSION360_VERSION.tar.gz" -o fusion360_sdk.tar.gz
    tar xzf fusion360_sdk.tar.gz
    mv fusion360_sdk "$INSTALL_DIR/"
    echo "export FUSION360_SDK_ROOT=$INSTALL_DIR/fusion360_sdk" >> ~/.zshrc
fi

# Clean up
rm -rf "$TEMP_DIR"

# Set up environment variables
export AUTODESK_SDK_ROOT="$INSTALL_DIR/aps_sdk"
export FUSION360_SDK_ROOT="$INSTALL_DIR/fusion360_sdk"

echo "Autodesk development environment setup complete!"
echo "Please restart your terminal or run: source ~/.zshrc"
