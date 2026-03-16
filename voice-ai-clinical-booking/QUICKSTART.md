# 🚀 Quick Start Guide

## ✅ Services are Running!

### Frontend
- **URL**: http://localhost:3000
- **Description**: Voice AI Interface with recording controls
- **Features**:
  - Multilingual support (English, Hindi, Tamil)
  - Real-time voice conversation
  - WebSocket communication
  - Latency metrics display
  - Conversation history

### Backend
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **WebSocket**: ws://localhost:8000/ws/{session_id}

## 📋 What You Can Do

### 1. Open the Frontend
```bash
open http://localhost:3000
```

### 2. Test the Voice Interface
- Click "Connect" button (phone icon)
- Select your language (English/Hindi/Tamil)
- Click microphone to start recording
- Speak your appointment request
- View real-time transcription and responses

### 3. Explore the API
```bash
open http://localhost:8000/docs
```

Available endpoints:
- `GET /health` - Health check
- `GET /api/doctors` - List doctors
- `GET /api/appointments` - List appointments
- `WS /ws/{session_id}` - Voice conversation

## 🔧 Management Commands

### View Logs
```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log
```

### Stop Services
```bash
bash stop.sh
```

### Restart Services
```bash
bash stop.sh && bash start.sh
```

## 🏗️ Project Structure

```
voice-ai-clinical-booking/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── agents/         # LangGraph voice agent
│   │   ├── api/            # REST & WebSocket endpoints
│   │   ├── core/           # Config, Celery tasks
│   │   ├── db/             # Database & Redis
│   │   ├── models/         # SQLAlchemy & Pydantic models
│   │   ├── services/       # STT, TTS, scheduling
│   │   └── tools/          # Agent tools
│   └── tests/              # Unit tests
│
├── frontend/               # Next.js frontend
│   └── src/
│       ├── app/            # Next.js pages
│       ├── components/     # React components
│       ├── hooks/          # Zustand store
│       ├── services/       # API & WebSocket clients
│       └── types/          # TypeScript types
│
├── docs/                   # Documentation
├── logs/                   # Application logs
├── start.sh               # Start all services
└── stop.sh                # Stop all services
```

## 🎯 Key Features Implemented

### ✅ Voice Pipeline
- Speech-to-Text (Whisper) - Ready
- Text-to-Speech (Coqui TTS) - Ready
- Language Detection - Ready
- WebSocket Communication - Working

### ✅ Agent System
- LangGraph orchestration - Implemented
- Tool-based reasoning - Implemented
- Multi-turn conversations - Supported
- Context management - Redis-based

### ✅ Scheduling Engine
- Conflict detection - Implemented
- Double booking prevention - Implemented
- Next available slots - Implemented
- Optimistic locking - Implemented

### ✅ Memory System
- Session memory (Redis) - Configured
- Long-term storage (PostgreSQL) - Schema ready
- Conversation history - Tracked

### ✅ Frontend
- Voice interface - Complete
- Language selection - Working
- Real-time updates - WebSocket
- Latency metrics - Displayed

## 🔄 Current Mode: DEMO

The application is running in **demo mode** without full database integration.

To enable full functionality:

1. **Start PostgreSQL**:
```bash
# Using Docker
docker run -d --name postgres \
  -e POSTGRES_USER=clinical_user \
  -e POSTGRES_PASSWORD=clinical_pass \
  -e POSTGRES_DB=clinical_ai \
  -p 5432:5432 postgres:15-alpine

# Or use local PostgreSQL
```

2. **Start Redis**:
```bash
# Using Docker
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Or use local Redis
```

3. **Initialize Database**:
```bash
cd backend
source venv/bin/activate
python -m app.db.init_db
```

4. **Add OpenAI API Key**:
Edit `backend/.env` and add your real OpenAI API key:
```
OPENAI_API_KEY=sk-your-real-key-here
```

5. **Restart Services**:
```bash
bash stop.sh && bash start.sh
```

## 📊 Performance Targets

- **STT Latency**: 80-120ms
- **LLM Latency**: 150-200ms
- **TTS Latency**: 100-150ms
- **Total Latency**: < 450ms

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill processes on ports
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### Backend Not Starting
```bash
# Check logs
cat logs/backend.log

# Verify Python environment
cd backend
source venv/bin/activate
python -c "from app.main_demo import app; print('OK')"
```

### Frontend Not Starting
```bash
# Check logs
cat logs/frontend.log

# Reinstall dependencies
cd frontend
rm -rf node_modules .next
npm install
```

## 📚 Next Steps

1. **Test Voice Interface**: Open http://localhost:3000
2. **Explore API**: Visit http://localhost:8000/docs
3. **Review Architecture**: See `docs/ARCHITECTURE.md`
4. **Run Tests**: `cd backend && pytest tests/`
5. **Enable Full Stack**: Follow database setup above

## 🎉 You're All Set!

The production-grade voice AI system is running and ready for testing.
