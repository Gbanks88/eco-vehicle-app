#!/bin/bash

# Application Builder for Eco Vehicle Project
# This script handles both C++ and Python components

set -e  # Exit on error

# Configuration
PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
BUILD_TYPE=${1:-Release}
PYTHON_ENV="venv"
INSTALL_PREFIX=${2:-/usr/local}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check system requirements
check_requirements() {
    log_info "Checking system requirements..."
    
    # Check CMake
    if ! command -v cmake &> /dev/null; then
        log_error "CMake is required but not installed."
        exit 1
    fi

    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed."
        exit 1
    fi

    # Check pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is required but not installed."
        exit 1
    }
}

# Setup Python environment
setup_python() {
    log_info "Setting up Python environment..."
    cd "$PROJECT_ROOT"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$PYTHON_ENV" ]; then
        python3 -m venv "$PYTHON_ENV"
    fi
    
    # Activate virtual environment
    source "$PYTHON_ENV/bin/activate"
    
    # Install requirements
    log_info "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r scripts/python/requirements.txt
}

# Build C++ components
build_cpp() {
    log_info "Building C++ components..."
    cd "$PROJECT_ROOT"
    
    # Create and enter build directory
    mkdir -p build
    cd build
    
    # Configure with CMake
    log_info "Configuring with CMake..."
    cmake .. \
        -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
        -DCMAKE_INSTALL_PREFIX=$INSTALL_PREFIX
    
    # Build
    log_info "Compiling..."
    cmake --build . --config $BUILD_TYPE -j$(nproc)
    
    # Run tests
    log_info "Running C++ tests..."
    ctest --output-on-failure
}

# Setup environment variables
setup_env() {
    log_info "Setting up environment variables..."
    cd "$PROJECT_ROOT"
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        cat > .env << EOL
# Eco Vehicle Project Environment Configuration
PYTHON_PATH=$PROJECT_ROOT/$PYTHON_ENV/bin/python3
CPP_BUILD_DIR=$PROJECT_ROOT/build
FUSION360_SCRIPTS_DIR=$PROJECT_ROOT/scripts/python/fusion360
MONITORING_SCRIPTS_DIR=$PROJECT_ROOT/scripts/python/monitoring
EOL
    fi
    
    # Source the environment variables
    set -a
    source .env
    set +a
}

# Main build process
main() {
    cd "$PROJECT_ROOT"
    
    log_info "Starting Eco Vehicle Project build process..."
    
    # Check requirements
    check_requirements
    
    # Setup Python
    setup_python
    
    # Build C++
    build_cpp
    
    # Setup environment
    setup_env
    
    log_info "Build process completed successfully!"
    log_info "You can now run the application using:"
    echo "  ./build/eco_vehicle"
    log_info "Python scripts are available in the virtual environment:"
    echo "  source $PYTHON_ENV/bin/activate"
}

# Run the main function
main

# Cleanup
deactivate 2>/dev/null || true  # Deactivate Python venv if active
