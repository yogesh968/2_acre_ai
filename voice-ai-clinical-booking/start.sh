#!/bin/bash

echo "=========================================="
echo "  Clinical Voice AI - Startup Script"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    lsof -ti:$1 > /dev/null 2>&1
}

# Kill existing processes
echo -e "${YELLOW}Checking for existing processes...${NC}"
if check_port 8000; then
    echo "Killing process on port 8000..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
fi

if check_port 3000; then
    echo "Killing process on port 3000..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null
fi

echo ""
echo -e "${BLUE}Starting Backend Server...${NC}"
cd backend
source venv/bin/activate
nohup uvicorn app.main_demo:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../logs/backend.pid
cd ..

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 3

# Check if backend is running
if check_port 8000; then
    echo -e "${GREEN}✅ Backend started successfully on http://localhost:8000${NC}"
    echo -e "   📚 API Docs: http://localhost:8000/docs"
else
    echo -e "${YELLOW}⚠️  Backend may not have started. Check logs/backend.log${NC}"
fi

echo ""
echo -e "${BLUE}Starting Frontend Server...${NC}"
cd frontend
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../logs/frontend.pid
cd ..

# Wait for frontend to start
echo "Waiting for frontend to start..."
sleep 5

# Check if frontend is running
if check_port 3000; then
    echo -e "${GREEN}✅ Frontend started successfully on http://localhost:3000${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend may not have started. Check logs/frontend.log${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🚀 Application is running!${NC}"
echo "=========================================="
echo ""
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Logs:"
echo "  Backend:  tail -f logs/backend.log"
echo "  Frontend: tail -f logs/frontend.log"
echo ""
echo "To stop all services, run: ./stop.sh"
echo ""
