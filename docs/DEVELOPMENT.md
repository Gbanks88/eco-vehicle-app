# Development Guide

## Getting Started

### Prerequisites
- CMake 3.15+
- Python 3.9+
- C++17 compliant compiler
- Docker (optional)
- Git

### Setting Up Development Environment

1. Clone the repository:
```bash
git clone <repository-url>
cd eco_vehicle_project
```

2. Run the setup script:
```bash
./scripts/shell/setup_dev_env.sh
```

3. Activate the Python virtual environment:
```bash
source venv/bin/activate
```

## Development Workflow

### Building the Project

1. Using CMake:
```bash
mkdir build && cd build
cmake ..
make -j$(nproc)
```

2. Using the build script:
```bash
./scripts/shell/build.sh Release
```

### Running Tests

1. All tests:
```bash
./scripts/shell/run_tests.sh
```

2. Specific test categories:
```bash
# C++ tests
cd build && ctest

# Python tests
pytest tests/

# Integration tests
python scripts/python/tests/integration_tests.py
```

### Code Quality

1. Linting:
```bash
# C++
clang-tidy src/*.cpp
cppcheck src/

# Python
pylint scripts/python/
black scripts/python/
```

2. Static Analysis:
```bash
# Security checks
bandit -r scripts/python/

# C++ analysis
scan-build make
```

## Project Structure

```
eco_vehicle_project/
├── .github/
│   └── workflows/        # CI/CD configurations
├── build/               # Build artifacts
├── config/              # Configuration files
├── data/                # Data files
├── docs/                # Documentation
├── logs/                # Log files
├── scripts/
│   ├── python/          # Python scripts
│   └── shell/           # Shell scripts
├── src/                 # C++ source code
│   ├── core/            # Core functionality
│   ├── modules/         # Project modules
│   └── tests/           # Test files
├── CMakeLists.txt      # CMake configuration
├── Dockerfile          # Docker configuration
└── README.md           # Project README
```

## Coding Standards

### C++
- Follow C++17 standards
- Use clang-format for code formatting
- Follow Google C++ Style Guide
- Document using Doxygen format

### Python
- Follow PEP 8 style guide
- Use type hints
- Document using Google docstring format
- Maintain test coverage above 80%

## Git Workflow

1. Branch naming:
   - feature/feature-name
   - bugfix/bug-description
   - hotfix/fix-description
   - release/version-number

2. Commit messages:
   - Use conventional commits format
   - Include ticket number if applicable
   - Keep messages clear and concise

3. Pull Requests:
   - Create PR against develop branch
   - Include description of changes
   - Reference related issues
   - Ensure all tests pass
   - Get code review approval

## Deployment

### Local Development
```bash
# Run locally
./build/bin/eco_vehicle

# Run with Docker
docker build -t eco-vehicle .
docker run -p 8080:8080 eco-vehicle
```

### Production Deployment
1. Automated via CI/CD pipeline
2. Triggered by merge to main branch
3. Includes:
   - Building
   - Testing
   - Security scanning
   - Docker image creation
   - Deployment to production

## Troubleshooting

### Common Issues

1. Build failures:
   - Check CMake version
   - Verify dependencies
   - Clear build directory

2. Test failures:
   - Check test logs
   - Verify environment setup
   - Review recent changes

3. Docker issues:
   - Check Docker daemon
   - Verify port availability
   - Review Docker logs

## Support

- Report issues on GitHub
- Contact development team
- Check documentation
