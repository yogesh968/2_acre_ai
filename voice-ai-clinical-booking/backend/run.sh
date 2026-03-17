#!/bin/bash

echo "=== Starting Clinical Voice AI Backend (Demo Mode) ==="

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Run setup.sh first."
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating demo .env file..."
    cat > .env << EOF
DATABASE_URL=postgresql://user:pass@localhost:5432/clinical_ai
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
OPENAI_API_KEY=sk-demo-key-replace-with-real-key
OPENAI_MODEL=gpt-4-turbo-preview
WHISPER_MODEL=base
LOG_LEVEL=INFO
DEBUG=True
EOF
fi

echo "Starting FastAPI server on http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""

uvicorn app.main_working:app --reload --host 0.0.0.0 --port 8000
