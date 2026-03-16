from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import get_settings
import json

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    print("🚀 Starting Clinical Voice AI application")
    print(f"📍 Server running on http://localhost:8000")
    print(f"📚 API Docs available at http://localhost:8000/docs")
    
    yield
    
    print("👋 Shutting down Clinical Voice AI application")

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket endpoint (simplified for demo)
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for voice communication"""
    await websocket.accept()
    print(f"✅ WebSocket connected: {session_id}")
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Echo back for demo
            if message["type"] == "audio_chunk":
                response = {
                    "type": "text",
                    "data": "Demo mode: Voice processing would happen here",
                    "metadata": {"role": "assistant"}
                }
                await websocket.send_text(json.dumps(response))
            
    except WebSocketDisconnect:
        print(f"❌ WebSocket disconnected: {session_id}")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "mode": "demo"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Clinical Voice AI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "websocket": "/ws/{session_id}"
    }

# Demo API endpoints
@app.get("/api/doctors")
async def get_doctors():
    """Get demo doctors"""
    return [
        {
            "id": "D1",
            "name": "Dr. Sarah Johnson",
            "specialization": "General Physician",
            "is_active": True
        },
        {
            "id": "D2",
            "name": "Dr. Raj Kumar",
            "specialization": "Cardiologist",
            "is_active": True
        }
    ]

@app.get("/api/appointments")
async def get_appointments():
    """Get demo appointments"""
    return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
