#!/bin/bash

# Customer Support Agent Startup Script
# This script starts all required services: MCP Server, FastAPI Server, and Streamlit UI

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Customer Support Agent Startup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo -e "${YELLOW}Please create a .env file with the following variables:${NC}"
    echo ""
    echo "HIGHFLAME_API_KEY=your_highflame_api_key"
    echo "HIGHFLAME_ROUTE=google  # or 'openai'"
    echo "MODEL=gemini-2.5-flash-lite  # or 'gpt-4o-mini' for OpenAI"
    echo "LLM_API_KEY=your_openai_or_gemini_api_key"
    echo "MCP_SERVER_URL=http://localhost:9000/mcp"
    echo "MCP_SERVER_HOST=0.0.0.0"
    echo "MCP_SERVER_PORT=9000"
    echo "DATABASE_PATH=./src/db/support_agent.db"
    echo "PORT=8000"
    echo ""
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 not found!${NC}"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

# Check if required packages are installed
echo -e "${YELLOW}Checking dependencies...${NC}"
if ! python3 -c "import fastapi, streamlit, langchain, fastmcp" 2>/dev/null; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
fi
echo -e "${GREEN}✓ Dependencies checked${NC}"
echo ""

# Create logs directory if it doesn't exist
mkdir -p logs

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process on a port
kill_port() {
    local port=$1
    local pid=$(lsof -ti :$port)
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}Killing process on port $port (PID: $pid)${NC}"
        kill -9 $pid 2>/dev/null || true
        sleep 1
    fi
}

# Check and free ports
echo -e "${YELLOW}Checking ports...${NC}"
if check_port 9000; then
    echo -e "${YELLOW}Port 9000 is in use. Attempting to free it...${NC}"
    kill_port 9000
fi

if check_port 8000; then
    echo -e "${YELLOW}Port 8000 is in use. Attempting to free it...${NC}"
    kill_port 8000
fi

if check_port 8501; then
    echo -e "${YELLOW}Port 8501 is in use. Attempting to free it...${NC}"
    kill_port 8501
fi

echo -e "${GREEN}✓ Ports checked${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down services...${NC}"
    # Kill background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

# Start MCP Server
echo -e "${BLUE}Starting MCP Server on port 9000...${NC}"
python3 -m src.mcp_server.server > logs/mcp_server.log 2>&1 &
MCP_PID=$!
sleep 3

# Check if MCP server started successfully
if ! kill -0 $MCP_PID 2>/dev/null; then
    echo -e "${RED}Error: MCP Server failed to start${NC}"
    echo "Check logs/mcp_server.log for details"
    exit 1
fi
echo -e "${GREEN}✓ MCP Server started (PID: $MCP_PID)${NC}"
echo ""

# Start FastAPI Server
echo -e "${BLUE}Starting FastAPI Server on port 8000...${NC}"
python3 -m uvicorn src.api:app --host 0.0.0.0 --port 8000 > logs/api_server.log 2>&1 &
API_PID=$!
sleep 3

# Check if API server started successfully
if ! kill -0 $API_PID 2>/dev/null; then
    echo -e "${RED}Error: FastAPI Server failed to start${NC}"
    echo "Check logs/api_server.log for details"
    kill $MCP_PID 2>/dev/null || true
    exit 1
fi
echo -e "${GREEN}✓ FastAPI Server started (PID: $API_PID)${NC}"
echo ""

# Start Streamlit UI
echo -e "${BLUE}Starting Streamlit UI on port 8501...${NC}"
cd src/ui
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > ../../logs/streamlit_ui.log 2>&1 &
UI_PID=$!
cd ../..
sleep 5

# Check if Streamlit started successfully
if ! kill -0 $UI_PID 2>/dev/null; then
    echo -e "${RED}Error: Streamlit UI failed to start${NC}"
    echo "Check logs/streamlit_ui.log for details"
    kill $MCP_PID $API_PID 2>/dev/null || true
    exit 1
fi
echo -e "${GREEN}✓ Streamlit UI started (PID: $UI_PID)${NC}"
echo ""

# Display service URLs
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}All services started successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Service URLs:${NC}"
echo -e "  ${GREEN}Streamlit UI:${NC}    http://localhost:8501"
echo -e "  ${GREEN}FastAPI Server:${NC}   http://localhost:8000"
echo -e "  ${GREEN}API Docs:${NC}         http://localhost:8000/docs"
echo -e "  ${GREEN}MCP Server:${NC}       http://localhost:9000/mcp"
echo ""
echo -e "${BLUE}Log Files:${NC}"
echo -e "  MCP Server:    logs/mcp_server.log"
echo -e "  API Server:   logs/api_server.log"
echo -e "  Streamlit UI: logs/streamlit_ui.log"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for all background processes
wait

