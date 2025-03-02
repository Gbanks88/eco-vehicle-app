#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Base directory
BASE_DIR="/Volumes/Learn_Space/eco_vehicle_project/web"
GAMES_DIR="$BASE_DIR/games"
LOG_DIR="$BASE_DIR/logs/games"

# Create logs directory
mkdir -p "$LOG_DIR"

# Function to start a game server
start_game_server() {
    local game=$1
    local port=$2
    local log_file="$LOG_DIR/${game// /_}.log"
    
    echo -e "${BLUE}Starting $game server on port $port...${NC}"
    
    cd "$GAMES_DIR/$game"
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Installing dependencies for $game...${NC}"
        npm install
    fi
    
    # Start the server
    PORT=$port npm start > "$log_file" 2>&1 &
    
    # Save PID
    echo $! > "$LOG_DIR/${game// /_}.pid"
    
    echo -e "${GREEN}$game server started on port $port${NC}"
}

# Function to stop a game server
stop_game_server() {
    local game=$1
    local pid_file="$LOG_DIR/${game// /_}.pid"
    
    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${BLUE}Stopping $game server...${NC}"
            kill "$pid"
            rm "$pid_file"
            echo -e "${GREEN}$game server stopped${NC}"
        else
            echo -e "${YELLOW}$game server was not running${NC}"
            rm "$pid_file"
        fi
    else
        echo -e "${YELLOW}No PID file found for $game${NC}"
    fi
}

# Function to check server status
check_server_status() {
    local game=$1
    local port=$2
    local pid_file="$LOG_DIR/${game// /_}.pid"
    
    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            if nc -z localhost "$port" 2>/dev/null; then
                echo -e "${GREEN}$game server is running on port $port (PID: $pid)${NC}"
                return 0
            else
                echo -e "${RED}$game server process exists but port $port is not responding${NC}"
                return 1
            fi
        else
            echo -e "${RED}$game server is not running${NC}"
            rm "$pid_file"
            return 1
        fi
    else
        echo -e "${RED}$game server is not running${NC}"
        return 1
    fi
}

# Game configurations
declare -A games=(
    ["motherboard_explorer"]="3001"
    ["recycling_challenge"]="3002"
    ["sysml_viewer"]="3003"
)

# Command processing
case "$1" in
    start)
        echo -e "${BLUE}Starting all game servers...${NC}"
        for game in "${!games[@]}"; do
            start_game_server "$game" "${games[$game]}"
        done
        ;;
    stop)
        echo -e "${BLUE}Stopping all game servers...${NC}"
        for game in "${!games[@]}"; do
            stop_game_server "$game"
        done
        ;;
    restart)
        echo -e "${BLUE}Restarting all game servers...${NC}"
        for game in "${!games[@]}"; do
            stop_game_server "$game"
            sleep 2
            start_game_server "$game" "${games[$game]}"
        done
        ;;
    status)
        echo -e "${BLUE}Checking game server status...${NC}"
        for game in "${!games[@]}"; do
            check_server_status "$game" "${games[$game]}"
        done
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac

exit 0
