FROM python:3.11-slim

WORKDIR /app

# Install minimal system dependencies (no ffmpeg/libsndfile needed for cloud-only)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy production requirements (lightweight, no PyTorch/Whisper/TTS)
COPY requirements-prod.txt .

# Install Python dependencies  
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run application (using $PORT for Render compatibility)
CMD ["sh", "-c", "uvicorn app.main_working:app --host 0.0.0.0 --port ${PORT:-8000}"]
