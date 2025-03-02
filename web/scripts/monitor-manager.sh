#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Base directory
BASE_DIR="/Volumes/Learn_Space/eco_vehicle_project/web"
SCRIPTS_DIR="$BASE_DIR/scripts"
LOG_DIR="$BASE_DIR/logs"
PID_DIR="$BASE_DIR/pids"

# Create necessary directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# Services to manage
SERVICES=(
    "advanced-monitor.sh"
    "auto-response.sh"
)

# Function to start a service
start_service() {
    local service=$1
    local pid_file="$PID_DIR/${service%.sh}.pid"
    local log_file="$LOG_DIR/${service%.sh}.log"
    
    if [ -f "$pid_file" ] && kill -0 $(cat "$pid_file") 2>/dev/null; then
        echo -e "${YELLOW}Service $service is already running${NC}"
        return
    fi
    
    echo -e "${BLUE}Starting $service...${NC}"
    nohup "$SCRIPTS_DIR/$service" > "$log_file" 2>&1 &
    echo $! > "$pid_file"
    echo -e "${GREEN}Started $service (PID: $(cat "$pid_file"))${NC}"
}

# Function to stop a service
stop_service() {
    local service=$1
    local pid_file="$PID_DIR/${service%.sh}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${BLUE}Stopping $service...${NC}"
            kill "$pid"
            rm "$pid_file"
            echo -e "${GREEN}Stopped $service${NC}"
        else
            echo -e "${YELLOW}Service $service is not running${NC}"
            rm "$pid_file"
        fi
    else
        echo -e "${YELLOW}No PID file found for $service${NC}"
    fi
}

# Function to check service status
check_status() {
    local service=$1
    local pid_file="$PID_DIR/${service%.sh}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${GREEN}$service is running (PID: $pid)${NC}"
            return 0
        else
            echo -e "${RED}$service is not running (stale PID file)${NC}"
            rm "$pid_file"
            return 1
        fi
    else
        echo -e "${RED}$service is not running${NC}"
        return 1
    fi
}

# Function to view logs
view_logs() {
    local service=$1
    local log_file="$LOG_DIR/${service%.sh}.log"
    
    if [ -f "$log_file" ]; then
        echo -e "${BLUE}Last 50 lines of $service logs:${NC}"
        tail -n 50 "$log_file"
    else
        echo -e "${RED}No log file found for $service${NC}"
    fi
}

# Function to rotate logs
rotate_logs() {
    local max_size=$((50*1024*1024)) # 50MB
    
    for log_file in "$LOG_DIR"/*.log; do
        if [ -f "$log_file" ]; then
            local size=$(stat -f%z "$log_file")
            if [ "$size" -gt "$max_size" ]; then
                echo -e "${BLUE}Rotating $log_file${NC}"
                mv "$log_file" "${log_file}.$(date +%Y%m%d-%H%M%S)"
                gzip "${log_file}.$(date +%Y%m%d-%H%M%S)"
            fi
        fi
    done
}

# Function to check disk space
check_disk_space() {
    local disk_usage=$(df -h "$LOG_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 90 ]; then
        echo -e "${RED}Warning: Low disk space ($disk_usage% used)${NC}"
        # Clean up old logs
        find "$LOG_DIR" -name "*.log.*.gz" -mtime +30 -delete
    fi
}

# Main command processing
case "$1" in
    start)
        if [ -n "$2" ]; then
            if [[ " ${SERVICES[@]} " =~ " $2 " ]]; then
                start_service "$2"
            else
                echo -e "${RED}Unknown service: $2${NC}"
            fi
        else
            for service in "${SERVICES[@]}"; do
                start_service "$service"
            done
        fi
        ;;
    stop)
        if [ -n "$2" ]; then
            if [[ " ${SERVICES[@]} " =~ " $2 " ]]; then
                stop_service "$2"
            else
                echo -e "${RED}Unknown service: $2${NC}"
            fi
        else
            for service in "${SERVICES[@]}"; do
                stop_service "$service"
            done
        fi
        ;;
    restart)
        if [ -n "$2" ]; then
            if [[ " ${SERVICES[@]} " =~ " $2 " ]]; then
                stop_service "$2"
                sleep 2
                start_service "$2"
            else
                echo -e "${RED}Unknown service: $2${NC}"
            fi
        else
            for service in "${SERVICES[@]}"; do
                stop_service "$service"
                sleep 2
                start_service "$service"
            done
        fi
        ;;
    status)
        if [ -n "$2" ]; then
            if [[ " ${SERVICES[@]} " =~ " $2 " ]]; then
                check_status "$2"
            else
                echo -e "${RED}Unknown service: $2${NC}"
            fi
        else
            for service in "${SERVICES[@]}"; do
                check_status "$service"
            done
        fi
        ;;
    logs)
        if [ -n "$2" ]; then
            if [[ " ${SERVICES[@]} " =~ " $2 " ]]; then
                view_logs "$2"
            else
                echo -e "${RED}Unknown service: $2${NC}"
            fi
        else
            for service in "${SERVICES[@]}"; do
                echo -e "\n${YELLOW}=== $service logs ===${NC}"
                view_logs "$service"
            done
        fi
        ;;
    rotate)
        rotate_logs
        ;;
    cleanup)
        check_disk_space
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|rotate|cleanup} [service]"
        echo "Available services:"
        printf "  %s\n" "${SERVICES[@]}"
        exit 1
        ;;
esac

exit 0
