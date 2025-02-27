#!/bin/bash

# Exit on error
set -e

# Configuration
BUILD_TYPE="Release"
BUILD_DIR="build"
INSTALL_DIR="install"
NUM_JOBS=$(sysctl -n hw.ncpu)

# Check required environment variables
if [ -z "$AUTODESK_SDK_ROOT" ]; then
    echo "Error: AUTODESK_SDK_ROOT environment variable not set"
    exit 1
fi

if [ -z "$FUSION360_SDK_ROOT" ]; then
    echo "Error: FUSION360_SDK_ROOT environment variable not set"
    exit 1
fi

# Print system information
echo "System Information:"
echo "- CPU Cores: $NUM_JOBS"
echo "- Build Type: $BUILD_TYPE"
echo "- Qt Version: $(qmake --version)"
echo "- Autodesk SDK: $AUTODESK_SDK_ROOT"
echo "- Fusion360 SDK: $FUSION360_SDK_ROOT"

# Create build directory
mkdir -p $BUILD_DIR
cd $BUILD_DIR

# Configure with CMake
echo "Configuring CMake..."
cmake .. \
    -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
    -DCMAKE_INSTALL_PREFIX=../$INSTALL_DIR \
    -DBUILD_TESTING=ON \
    -DENABLE_CUDA=ON \
    -DENABLE_OPTIMIZATION=ON \
    -DENABLE_PROFILING=ON

# Build
echo "Building with $NUM_JOBS jobs..."
cmake --build . --config $BUILD_TYPE -j $NUM_JOBS

# Run tests
echo "Running tests..."
ctest --output-on-failure

# Install
echo "Installing..."
cmake --install .

echo "Build completed successfully!"
