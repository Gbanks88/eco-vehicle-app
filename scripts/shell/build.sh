#!/bin/bash

# Build script for eco-vehicle project

# Exit on error
set -e

# Configuration
BUILD_DIR="build"
BUILD_TYPE=${1:-Release}  # Default to Release if not specified
INSTALL_PREFIX=${2:-/usr/local}

# Create and enter build directory
mkdir -p $BUILD_DIR
cd $BUILD_DIR

# Configure with CMake
echo "Configuring project with CMake..."
cmake .. \
    -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
    -DCMAKE_INSTALL_PREFIX=$INSTALL_PREFIX

# Build the project
echo "Building project..."
cmake --build . --config $BUILD_TYPE -j$(nproc)

# Run tests
echo "Running tests..."
ctest --output-on-failure

# Install if requested
if [ "$3" = "install" ]; then
    echo "Installing..."
    cmake --install .
fi

echo "Build complete!"
