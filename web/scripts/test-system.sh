#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Base directory
BASE_DIR="/Volumes/Learn_Space/eco_vehicle_project/web"
LOG_DIR="$BASE_DIR/logs"
TEST_LOG="$LOG_DIR/test-results.log"

# Create logs directory
mkdir -p "$LOG_DIR"

# Function to log results
log_result() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$TEST_LOG"
    echo -e "$2$1${NC}"
}

# Function to test API endpoint
test_endpoint() {
    local endpoint=$1
    local method=${2:-GET}
    local data=$3
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "%{http_code}" "http://localhost:3000$endpoint")
    else
        response=$(curl -s -w "%{http_code}" -X "$method" -H "Content-Type: application/json" -d "$data" "http://localhost:3000$endpoint")
    fi
    
    http_code=${response: -3}
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        log_result "✓ $method $endpoint - Success ($http_code)" "${GREEN}"
        return 0
    else
        log_result "✗ $method $endpoint - Failed ($http_code)" "${RED}"
        return 1
    fi
}

# Function to test MongoDB connection
test_mongodb() {
    echo -e "${YELLOW}Testing MongoDB connection...${NC}"
    if mongosh --eval "db.adminCommand('ping')" &>/dev/null; then
        log_result "✓ MongoDB connection successful" "${GREEN}"
        return 0
    else
        log_result "✗ MongoDB connection failed" "${RED}"
        return 1
    fi
}

# Function to test security headers
test_security_headers() {
    echo -e "${YELLOW}Testing security headers...${NC}"
    local headers=$(curl -sI "http://localhost:3000")
    
    local required_headers=(
        "Strict-Transport-Security"
        "Content-Security-Policy"
        "X-Frame-Options"
        "X-Content-Type-Options"
    )
    
    local success=true
    for header in "${required_headers[@]}"; do
        if echo "$headers" | grep -q "$header"; then
            log_result "✓ $header header present" "${GREEN}"
        else
            log_result "✗ $header header missing" "${RED}"
            success=false
        fi
    done
    
    $success && return 0 || return 1
}

# Function to test monitoring system
test_monitoring() {
    echo -e "${YELLOW}Testing monitoring system...${NC}"
    
    # Check if monitoring processes are running
    if pgrep -f "monitor-manager.sh" > /dev/null; then
        log_result "✓ Monitoring system is running" "${GREEN}"
    else
        log_result "✗ Monitoring system is not running" "${RED}"
        return 1
    fi
    
    # Check log files
    if [ -d "$LOG_DIR/metrics" ] && [ "$(ls -A $LOG_DIR/metrics)" ]; then
        log_result "✓ Metrics are being collected" "${GREEN}"
    else
        log_result "✗ No metrics found" "${RED}"
        return 1
    fi
    
    return 0
}

# Function to test backup system
test_backup() {
    echo -e "${YELLOW}Testing backup system...${NC}"
    
    # Test backup creation
    ./scripts/backup-manager.sh daily
    
    if [ -d "$BASE_DIR/backups/daily" ] && [ "$(ls -A $BASE_DIR/backups/daily)" ]; then
        log_result "✓ Backup system is working" "${GREEN}"
        return 0
    else
        log_result "✗ Backup system failed" "${RED}"
        return 1
    fi
}

# Function to test game servers
test_game_servers() {
    echo -e "${YELLOW}Testing game servers...${NC}"
    
    local game_ports=(
        "3001:Motherboard Explorer"
        "3002:Recycling Challenge"
        "3003:SysML Viewer"
    )
    
    local success=true
    for port_game in "${game_ports[@]}"; do
        IFS=':' read -r port game <<< "$port_game"
        if nc -z localhost "$port" 2>/dev/null; then
            log_result "✓ $game server is running (Port: $port)" "${GREEN}"
        else
            log_result "✗ $game server is not running (Port: $port)" "${RED}"
            success=false
        fi
    done
    
    $success && return 0 || return 1
}

# Main testing process
echo -e "${BLUE}Starting system tests...${NC}"
echo "Test started at $(date)" > "$TEST_LOG"

# Array to track test results
declare -A test_results

# Run all tests
test_mongodb
test_results["MongoDB"]=$?

test_security_headers
test_results["Security"]=$?

test_monitoring
test_results["Monitoring"]=$?

test_backup
test_results["Backup"]=$?

test_game_servers
test_results["Games"]=$?

# Test API endpoints
echo -e "${YELLOW}Testing API endpoints...${NC}"
test_endpoint "/api/auth/session" "GET"
test_results["Auth API"]=$?

test_endpoint "/api/vehicles" "GET"
test_results["Vehicles API"]=$?

test_endpoint "/api/games/scores" "GET"
test_results["Games API"]=$?

# Summary
echo -e "\n${BLUE}Test Summary:${NC}"
failures=0
for test in "${!test_results[@]}"; do
    if [ "${test_results[$test]}" -eq 0 ]; then
        echo -e "${GREEN}✓ $test: Passed${NC}"
    else
        echo -e "${RED}✗ $test: Failed${NC}"
        ((failures++))
    fi
done

# Final result
echo -e "\n${YELLOW}Test Results:${NC}"
if [ "$failures" -eq 0 ]; then
    echo -e "${GREEN}All tests passed successfully!${NC}"
    exit 0
else
    echo -e "${RED}$failures test(s) failed. Check $TEST_LOG for details.${NC}"
    exit 1
fi
