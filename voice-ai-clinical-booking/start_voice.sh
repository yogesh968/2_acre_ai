#!/bin/bash

echo "=========================================="
echo "  Clinical Voice AI - Starting Services"
echo "=========================================="
echo ""

# Kill existing processes
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
sleep 2

echo "🚀 Starting Backend (Voice-Enabled)..."
cd backend
source venv/bin/activate
python -m uvicorn app.main_voice_complete:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../logs/backend.pid
cd ..

sleep 5

# Check backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend started on http://localhost:8000"
else
    echo "⚠️  Backend may not be ready yet..."
fi

echo ""
echo "🚀 Starting Frontend..."
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../logs/frontend.pid
cd ..

sleep 5

# Check frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend started on http://localhost:3000"
else
    echo "⚠️  Frontend may not be ready yet..."
fi

echo ""
echo "=========================================="
echo "✅ Services Started!"
echo "=========================================="
echo ""
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Features:"
echo "  🎤 Voice Input: Enabled"
echo "  🔊 Voice Output: Enabled (gTTS)"
echo "  🤖 AI: GPT-4o-mini"
echo "  🌐 Languages: English, Hindi, Tamil"
echo ""
echo "Logs:"
echo "  tail -f logs/backend.log"
echo "  tail -f logs/frontend.log"
echo ""
