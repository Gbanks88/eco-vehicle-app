#!/bin/bash

# Development Environment Setup Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Setting up development environment...${NC}"

# Check operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS setup
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install dependencies
    brew install cmake
    brew install boost
    brew install opencv
    brew install eigen
    brew install grpc
    brew install sqlite
    brew install paho-mqtt
    brew install python@3.9
    brew install node
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux setup
    sudo apt-get update
    sudo apt-get install -y \
        build-essential \
        cmake \
        libboost-all-dev \
        libopencv-dev \
        libeigen3-dev \
        libgrpc++-dev \
        libsqlite3-dev \
        libpaho-mqtt-dev \
        python3.9 \
        python3.9-dev \
        nodejs
fi

# Create Python virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r scripts/python/requirements.txt

# Setup git hooks
mkdir -p .git/hooks
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Run tests before commit
./scripts/shell/run_tests.sh
EOF
chmod +x .git/hooks/pre-commit

# Create necessary directories
mkdir -p \
    build \
    data \
    logs \
    docs/api \
    src/tests \
    config/environments

echo -e "${GREEN}Development environment setup complete!${NC}"
