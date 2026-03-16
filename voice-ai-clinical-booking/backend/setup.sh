#!/bin/bash

echo "=== Clinical Voice AI Backend Setup ==="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your OPENAI_API_KEY"
fi

# Download Whisper model
echo "Downloading Whisper model (this may take a moment)..."
python -c "import whisper; whisper.load_model('base')" 2>/dev/null || echo "Whisper model already downloaded"

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the backend:"
echo "1. Make sure PostgreSQL is running on localhost:5432"
echo "2. Make sure Redis is running on localhost:6379"
echo "3. Run: source venv/bin/activate"
echo "4. Run: python -m app.db.init_db  (first time only)"
echo "5. Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
