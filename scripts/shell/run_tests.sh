#!/bin/bash

# Test Runner Script for Requirements Bot and Complex Systems
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
TEST_OUTPUT_DIR="test_results"
COVERAGE_THRESHOLD=80
PERFORMANCE_THRESHOLD=2000  # milliseconds

echo -e "${GREEN}Starting Comprehensive Test Suite...${NC}"

# Create test output directory structure
mkdir -p "$TEST_OUTPUT_DIR"/{unit,integration,performance,validation}

# Function to run tests with timing
run_timed_tests() {
    local test_type=$1
    local test_path=$2
    local output_file=$3
    
    echo -e "\n${BLUE}Running $test_type tests...${NC}"
    start_time=$(date +%s%N)
    
    pytest "$test_path" \
        --cov=src \
        --cov-report=html:"$TEST_OUTPUT_DIR/$test_type/coverage" \
        --cov-report=xml:"$TEST_OUTPUT_DIR/$test_type/coverage.xml" \
        --junit-xml="$TEST_OUTPUT_DIR/$test_type/results.xml" \
        -v
    
    end_time=$(date +%s%N)
    duration=$((($end_time - $start_time)/1000000)) # Convert to milliseconds
    
    echo -e "${GREEN}$test_type tests completed in ${duration}ms${NC}"
    
    # Check performance threshold for performance tests
    if [ "$test_type" = "performance" ] && [ $duration -gt $PERFORMANCE_THRESHOLD ]; then
        echo -e "${RED}Warning: Performance tests exceeded threshold of ${PERFORMANCE_THRESHOLD}ms${NC}"
    fi
}

# Run unit tests
run_timed_tests "unit" "tests/unit" "unit_tests.log"

# Run integration tests
run_timed_tests "integration" "tests/integration" "integration_tests.log"

# Run performance tests
run_timed_tests "performance" "tests/performance" "performance_tests.log"

# Run validation tests
run_timed_tests "validation" "tests/validation" "validation_tests.log"

# Generate comprehensive test report
echo -e "\n${YELLOW}Generating comprehensive test report...${NC}"
python scripts/python/utils/generate_test_report.py \
    --unit-results "$TEST_OUTPUT_DIR/unit/results.xml" \
    --integration-results "$TEST_OUTPUT_DIR/integration/results.xml" \
    --performance-results "$TEST_OUTPUT_DIR/performance/results.xml" \
    --validation-results "$TEST_OUTPUT_DIR/validation/results.xml" \
    --unit-coverage "$TEST_OUTPUT_DIR/unit/coverage.xml" \
    --output "$TEST_OUTPUT_DIR/comprehensive_report.html"

# Check overall coverage
echo -e "\n${YELLOW}Checking overall coverage...${NC}"
coverage_percent=$(python -c "
import xml.etree.ElementTree as ET
tree = ET.parse('$TEST_OUTPUT_DIR/unit/coverage.xml')
root = tree.getroot()
print(float(root.attrib['line-rate']) * 100)
")

if (( $(echo "$coverage_percent < $COVERAGE_THRESHOLD" | bc -l) )); then
    echo -e "${RED}Coverage ${coverage_percent}% below threshold of ${COVERAGE_THRESHOLD}%${NC}"
    exit 1
else
    echo -e "${GREEN}Coverage ${coverage_percent}% meets threshold of ${COVERAGE_THRESHOLD}%${NC}"
fi

echo -e "\n${GREEN}All tests completed successfully!${NC}"

echo -e "${GREEN}All tests completed!${NC}"
