#!/bin/bash

# --- INTERNAL CONFIGURATION (Prefixing to avoid .env collisions) ---
readonly INT_BE_PORT=8000
readonly INT_FE_PORT=5173
readonly INT_DB_PORT=5432
readonly INT_HEALTH_URL="http://localhost:$INT_BE_PORT/docs"
readonly INT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- COLORS ---
readonly CLR_BE='\033[0;34m'
readonly CLR_FE='\033[0;35m'
readonly CLR_SYS='\033[0;32m'
readonly CLR_ERR='\033[0;31m'
readonly CLR_WARN='\033[0;33m'
readonly NC='\033[0m'

# --- LOG TRANSFORMER ---
format_log() {
    local tag=$1
    local color=$2
    local module=$3
    while IFS= read -r line; do
        if [ -n "$line" ]; then
            local timestamp=$(date +'%H:%M:%S')
            
            # Detect log level from message
            local level="INFO"
            local status="SUCCESS"
            if echo "$line" | grep -qiE '(warn|warning|deprecated)'; then
                level="WARN"
                status="DEPRECATION"
                color=$CLR_WARN
            elif echo "$line" | grep -qiE '(error|fail|fatal)'; then
                level="ERROR"
                status="FAILURE"
                color=$CLR_ERR
            fi
            
            # Clean up raw uvicorn/vite noise
            local clean_line=$(echo "$line" | sed -E 's/^(INFO|DEBUG|WARNING|ERROR|[\^[:space:]]+):[[:space:]]*//')
            
            echo -e "${color}[$tag] [$level] [$timestamp] [$module] [$status]:${NC} $clean_line"
        fi
    done
}

sys_log() {
    local timestamp=$(date +'%H:%M:%S')
    local level="${4:-INFO}"
    local color=$CLR_SYS
    [[ $level == "ERROR" ]] && color=$CLR_ERR
    echo -e "${color}[SYS] [$level] [$timestamp] [$1] [$2]: $3${NC}"
}

# --- ENVIRONMENT LOADER ---
load_env() {
    local env_file="$1"
    if [ -f "$env_file" ]; then
        set -a; source "$env_file"; set +a
    fi
}

cleanup() {
    echo ""
    sys_log "SYSTEM" "EXIT" "Initiating graceful shutdown..."
    [[ -n $BE_PID ]] && kill -TERM -"$BE_PID" 2>/dev/null
    [[ -n $FE_PID ]] && kill -TERM -"$FE_PID" 2>/dev/null
    lsof -ti:"$INT_BE_PORT","$INT_FE_PORT" | xargs kill -9 2>/dev/null || true
    sys_log "SYSTEM" "CLEAN" "Cleanup complete."
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

print_banner() {
    echo -e "${CLR_SYS}"
    echo "|-----------------------------------------------|"
    echo "|     ASC-Scheduler Started Successfully        |"
    echo "|-----------------------------------------------|"
    echo "|  Database:      ✓ localhost:$INT_DB_PORT              |"
    echo "|  Backend API:   ✓ http://localhost:$INT_BE_PORT       |"
    echo "|  Backend Docs:  ✓ http://localhost:$INT_BE_PORT/docs  |"
    echo "|  Frontend:      ✓ http://localhost:$INT_FE_PORT       |"
    echo "|-----------------------------------------------|"
    echo -e "${NC}"
}

# --- STARTUP LOGIC ---
clear
sys_log "SYSTEM" "START" "ASC-Scheduler Full Stack Boot"

# 1. Database Pre-check
if ! nc -z localhost $INT_DB_PORT; then
    sys_log "DATABASE" "ERROR" "Postgres not found on $INT_DB_PORT. Please start your DB." "ERROR"
    exit 1
fi
sys_log "DATABASE" "CONNECTED" "PostgreSQL connection verified on port $INT_DB_PORT"

# 2. Port Cleanup
lsof -ti:"$INT_BE_PORT","$INT_FE_PORT" | xargs kill -9 2>/dev/null || true

# 3. Start Backend
set -m
run_backend() {
    cd "$INT_ROOT/backend" || exit 1
    load_env ".env"
    
    # Virtual Env Check
    if [ ! -d ".venv" ]; then
        sys_log "BACKEND" "VENV" "Creating virtual environment..."
        python3 -m venv .venv
    fi
    source .venv/bin/activate
    
    sys_log "BACKEND" "DEPS" "Checking dependencies..."
    pip install -q -r requirements.txt
    
    # Run Uvicorn and pipe to transformer
    exec uvicorn app.main:app --host 0.0.0.0 --port $INT_BE_PORT --reload 2>&1 | format_log "BE" "$CLR_BE" "API"
}
run_backend &
BE_PID=$!

# 4. Smart Health Check
sys_log "SYSTEM" "WAIT" "Waiting for Backend API at $INT_HEALTH_URL..."
ATTEMPTS=0
MAX_ATTEMPTS=20
until $(curl --output /dev/null --silent --head --fail "$INT_HEALTH_URL"); do
    printf "${CLR_BE}.${NC}"
    sleep 1
    ((ATTEMPTS++))
    if [ $ATTEMPTS -eq $MAX_ATTEMPTS ]; then
        echo -e "\n"
        sys_log "SYSTEM" "TIMEOUT" "Backend failed health check. Run 'cd backend && uvicorn app.main:app' to see errors." "ERROR"
        exit 1
    fi
done
echo -e "\n"
sys_log "SYSTEM" "READY" "Backend is alive and healthy."

# 5. Start Frontend
run_frontend() {
    cd "$INT_ROOT/frontend" || exit 1
    load_env ".env"
    [[ ! -d "node_modules" ]] && sys_log "FRONTEND" "INSTALL" "Running npm install..." && npm install --silent
    
    exec npm run dev -- --port $INT_FE_PORT 2>&1 | format_log "FE" "$CLR_FE" "VITE"
}
run_frontend &
FE_PID=$!

# 6. Wait for frontend to be ready
sleep 2

# 7. Print success banner
print_banner

# Stay alive
wait
