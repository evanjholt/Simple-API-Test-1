#!/bin/bash

# ngrok Shell Deployment Script for Simple API Test Application
# Alternative deployment method using ngrok CLI directly
#
# Prerequisites:
# 1. Install ngrok: https://ngrok.com/download
# 2. Install Python dependencies: pip install -r requirements.txt
#
# Usage:
#   ./ngrok_deploy.sh [PORT] [AUTH_TOKEN]
#   
# Examples:
#   ./ngrok_deploy.sh                    # Use default port 8000
#   ./ngrok_deploy.sh 8080              # Use port 8080
#   ./ngrok_deploy.sh 8000 your_token   # Use port 8000 with auth token

set -e

# Configuration
PORT=${1:-8000}
AUTH_TOKEN=${2:-""}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🔄 Shutting down...${NC}"
    
    # Kill FastAPI server
    if [[ ! -z "$FASTAPI_PID" ]]; then
        echo -e "${GREEN}✅ Stopping FastAPI server (PID: $FASTAPI_PID)${NC}"
        kill $FASTAPI_PID 2>/dev/null || true
    fi
    
    # Kill ngrok
    pkill -f "ngrok http" 2>/dev/null || true
    echo -e "${GREEN}✅ Stopped ngrok tunnel${NC}"
    
    echo -e "${PURPLE}👋 Deployment stopped${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo -e "${CYAN}🔧 Simple API Test - ngrok Deployment${NC}"
echo -e "${CYAN}====================================${NC}"

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo -e "${RED}❌ ngrok not found!${NC}"
    echo -e "${YELLOW}📥 Install from: https://ngrok.com/download${NC}"
    exit 1
fi

# Check if Python dependencies are installed
if ! python -c "import fastapi, uvicorn" &> /dev/null; then
    echo -e "${RED}❌ Python dependencies missing!${NC}"
    echo -e "${YELLOW}📦 Run: pip install -r requirements.txt${NC}"
    exit 1
fi

# Set ngrok auth token if provided
if [[ ! -z "$AUTH_TOKEN" ]]; then
    echo -e "${GREEN}🔑 Setting ngrok auth token...${NC}"
    ngrok config add-authtoken "$AUTH_TOKEN"
fi

# Start FastAPI server in background
echo -e "${BLUE}🚀 Starting FastAPI server on port $PORT...${NC}"
cd "$SCRIPT_DIR"
python -c "
import uvicorn
from main import app
uvicorn.run(app, host='127.0.0.1', port=$PORT, log_level='info')
" &

FASTAPI_PID=$!
echo -e "${GREEN}✅ FastAPI server started (PID: $FASTAPI_PID)${NC}"

# Wait for server to start
sleep 3

# Check if server is running
if ! kill -0 $FASTAPI_PID 2>/dev/null; then
    echo -e "${RED}❌ FastAPI server failed to start${NC}"
    exit 1
fi

# Start ngrok tunnel
echo -e "${BLUE}🌐 Creating ngrok tunnel...${NC}"
ngrok http $PORT --log=stdout > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!

# Wait for ngrok to establish tunnel
sleep 5

# Extract public URL from ngrok
PUBLIC_URL=""
for i in {1..10}; do
    if command -v curl &> /dev/null; then
        PUBLIC_URL=$(curl -s http://localhost:4040/api/tunnels | python -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(data['tunnels'][0]['public_url'])
except:
    pass
" 2>/dev/null)
    fi
    
    if [[ ! -z "$PUBLIC_URL" ]]; then
        break
    fi
    
    echo -e "${YELLOW}⏳ Waiting for ngrok tunnel... (attempt $i/10)${NC}"
    sleep 2
done

if [[ -z "$PUBLIC_URL" ]]; then
    echo -e "${RED}❌ Failed to get ngrok public URL${NC}"
    echo -e "${YELLOW}💡 Check ngrok logs at: /tmp/ngrok.log${NC}"
    cleanup
fi

# Display deployment information
echo -e "\n${GREEN}============================================================${NC}"
echo -e "${GREEN}🌐 API DEPLOYED WITH NGROK${NC}"
echo -e "${GREEN}============================================================${NC}"
echo -e "${BLUE}📍 Local URL:     ${NC}http://localhost:$PORT"
echo -e "${PURPLE}🔗 Public URL:    ${NC}$PUBLIC_URL"
echo -e "${CYAN}📚 API Docs:      ${NC}$PUBLIC_URL/docs"
echo -e "${CYAN}📖 ReDoc:         ${NC}$PUBLIC_URL/redoc"
echo -e "${CYAN}💓 Health Check:  ${NC}$PUBLIC_URL/health"
echo -e "${GREEN}============================================================${NC}"
echo -e "\n${YELLOW}🔧 TESTING ENDPOINTS:${NC}"
echo -e "  ${BLUE}Users:     ${NC}$PUBLIC_URL/users"
echo -e "  ${BLUE}Items:     ${NC}$PUBLIC_URL/items"
echo -e "  ${BLUE}Root:      ${NC}$PUBLIC_URL/"
echo -e "\n${PURPLE}💡 Use these URLs in your external testing programs!${NC}"
echo -e "\n${RED}⚠️  Press Ctrl+C to stop the deployment${NC}"
echo -e "${GREEN}------------------------------------------------------------${NC}"

# Keep running until interrupted
while true; do
    # Check if FastAPI server is still running
    if ! kill -0 $FASTAPI_PID 2>/dev/null; then
        echo -e "${RED}❌ FastAPI server stopped unexpectedly${NC}"
        cleanup
    fi
    
    sleep 5
done