#!/bin/bash

echo "Stopping Clinical Voice AI services..."

# Kill backend
if [ -f logs/backend.pid ]; then
    PID=$(cat logs/backend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo "✅ Backend stopped (PID: $PID)"
    fi
    rm logs/backend.pid
fi

# Kill frontend
if [ -f logs/frontend.pid ]; then
    PID=$(cat logs/frontend.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo "✅ Frontend stopped (PID: $PID)"
    fi
    rm logs/frontend.pid
fi

# Kill any remaining processes on ports
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

echo "✅ All services stopped"
