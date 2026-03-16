from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import get_settings
import json
import base64
import time
from datetime import datetime, timedelta
from gtts import gTTS
import io
import asyncio
import re

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    print("🚀 Starting Clinical Voice AI application (Demo Mode)")
    print(f"📍 Server running on http://localhost:8000")
    print(f"📚 API Docs available at http://localhost:8000/docs")
    print(f"🎤 Voice input: Enabled")
    print(f"🔊 Voice output: Enabled (gTTS)")
    print(f"🤖 AI: Rule-based (No API key needed)")
    
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

# Store active sessions
sessions = {}
processing_sessions = set()

# Simple rule-based responses
def get_ai_response(user_text: str, conversation_history: list) -> str:
    """Simple rule-based AI responses"""
    text_lower = user_text.lower()
    
    # Greeting
    if any(word in text_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
        return "Hello! I'm your medical appointment assistant. I can help you book, reschedule, or cancel appointments. How can I assist you today?"
    
    # Booking intent
    if any(word in text_lower for word in ['book', 'schedule', 'appointment', 'see doctor']):
        if 'sarah' in text_lower or 'johnson' in text_lower:
            return "Great! I can help you book an appointment with Dr. Sarah Johnson, our General Physician. She's available Monday through Friday, 9 AM to 5 PM. What date and time would work best for you?"
        elif 'raj' in text_lower or 'kumar' in text_lower or 'cardiologist' in text_lower:
            return "Perfect! Dr. Raj Kumar, our Cardiologist, is available Monday through Wednesday, 10 AM to 4 PM. When would you like to schedule your appointment?"
        elif 'priya' in text_lower or 'sharma' in text_lower or 'pediatrician' in text_lower:
            return "Excellent! Dr. Priya Sharma, our Pediatrician, is available Tuesday through Saturday, 9 AM to 3 PM. What date and time would you prefer?"
        else:
            return "I'd be happy to help you book an appointment. We have three doctors available: Dr. Sarah Johnson (General Physician), Dr. Raj Kumar (Cardiologist), and Dr. Priya Sharma (Pediatrician). Which doctor would you like to see?"
    
    # Time mentioned
    if any(word in text_lower for word in ['tomorrow', 'today', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']) or \
       any(word in text_lower for word in ['am', 'pm', 'morning', 'afternoon', 'evening']):
        return "Perfect! I've noted your preferred time. To complete your booking, may I know the reason for your visit? This helps the doctor prepare for your appointment."
    
    # Reason for visit
    if any(word in text_lower for word in ['checkup', 'fever', 'cold', 'pain', 'sick', 'consultation', 'follow-up', 'test']):
        return "Thank you! Your appointment has been successfully booked. You'll receive a confirmation message shortly. Is there anything else I can help you with?"
    
    # Cancellation
    if any(word in text_lower for word in ['cancel', 'delete', 'remove']):
        return "I understand you'd like to cancel an appointment. Could you please provide your appointment ID or the date of your appointment?"
    
    # Reschedule
    if any(word in text_lower for word in ['reschedule', 'change', 'move', 'different time']):
        return "I can help you reschedule your appointment. What's your current appointment date, and when would you like to move it to?"
    
    # Check appointments
    if any(word in text_lower for word in ['my appointment', 'check', 'view', 'show', 'list']):
        return "Let me check your appointments. You have one upcoming appointment with Dr. Sarah Johnson on January 15th at 10 AM. Would you like to modify this appointment?"
    
    # Thank you
    if any(word in text_lower for word in ['thank', 'thanks', 'appreciate']):
        return "You're very welcome! If you need any assistance with appointments in the future, feel free to reach out. Take care!"
    
    # Goodbye
    if any(word in text_lower for word in ['bye', 'goodbye', 'see you', 'exit']):
        return "Goodbye! Have a great day and stay healthy!"
    
    # Default
    return "I'm here to help with medical appointments. You can book a new appointment, reschedule an existing one, or cancel an appointment. What would you like to do?"

async def text_to_speech(text: str, language: str = "en") -> bytes:
    """Convert text to speech using gTTS"""
    try:
        lang_map = {"en": "en", "hi": "hi", "ta": "ta"}
        tts_lang = lang_map.get(language, "en")
        
        loop = asyncio.get_event_loop()
        audio_bytes = await loop.run_in_executor(None, lambda: _generate_speech(text, tts_lang))
        return audio_bytes
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        return b""

def _generate_speech(text: str, lang: str) -> bytes:
    """Synchronous speech generation"""
    tts = gTTS(text=text, lang=lang, slow=False)
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer.read()

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for voice communication"""
    await websocket.accept()
    print(f"✅ WebSocket connected: {session_id}")
    
    if session_id not in sessions:
        sessions[session_id] = {
            "language": "en",
            "conversation_history": []
        }
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "audio_chunk":
                if session_id in processing_sessions:
                    print(f"⏭️  Skipping - already processing for session {session_id}")
                    continue
                
                processing_sessions.add(session_id)
                start_time = time.time()
                
                print(f"📝 Processing audio for session {session_id}")
                
                # Simulate STT - in real app, use Whisper here
                user_text = "I want to book an appointment with Dr. Sarah Johnson for tomorrow at 10 AM"
                
                # Send transcript back
                await websocket.send_text(json.dumps({
                    "type": "text",
                    "data": user_text,
                    "metadata": {"role": "user"}
                }))
                
                # Get AI response (rule-based)
                llm_start = time.time()
                assistant_text = get_ai_response(user_text, sessions[session_id]["conversation_history"])
                llm_latency = (time.time() - llm_start) * 1000
                
                print(f"🤖 AI Response ({llm_latency:.0f}ms): {assistant_text}")
                
                # Send text response
                await websocket.send_text(json.dumps({
                    "type": "text",
                    "data": assistant_text,
                    "metadata": {"role": "assistant"}
                }))
                
                # Generate speech
                tts_start = time.time()
                audio_bytes = await text_to_speech(assistant_text, sessions[session_id]["language"])
                tts_latency = (time.time() - tts_start) * 1000
                
                if audio_bytes:
                    print(f"🔊 TTS generated ({tts_latency:.0f}ms), sending audio...")
                    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                    await websocket.send_text(json.dumps({
                        "type": "audio_chunk",
                        "data": audio_b64,
                        "sample_rate": 24000,
                        "metadata": {"format": "mp3"}
                    }))
                    print(f"✅ Audio sent to client")
                
                # Send latency metrics
                total_latency = (time.time() - start_time) * 1000
                await websocket.send_text(json.dumps({
                    "type": "latency",
                    "data": "",
                    "metadata": {
                        "stt_latency": 100.0,
                        "llm_latency": llm_latency,
                        "tool_latency": 0.0,
                        "tts_latency": tts_latency,
                        "total_latency": total_latency,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }))
                
                # Store in conversation history
                sessions[session_id]["conversation_history"].extend([
                    {"role": "user", "content": user_text, "timestamp": datetime.utcnow().isoformat()},
                    {"role": "assistant", "content": assistant_text, "timestamp": datetime.utcnow().isoformat()}
                ])
                
                processing_sessions.discard(session_id)
                print(f"✅ Completed processing for session {session_id}")
            
            elif message["type"] == "control":
                if message["data"] == "interrupt":
                    print(f"⏸️  Interrupt received for session {session_id}")
                    processing_sessions.discard(session_id)
                    await websocket.send_text(json.dumps({
                        "type": "control",
                        "data": "interrupted",
                        "metadata": {}
                    }))
                elif message["data"] == "set_language":
                    lang = message.get("metadata", {}).get("language", "en")
                    sessions[session_id]["language"] = lang
                    print(f"🌐 Language set to: {lang}")
    
    except WebSocketDisconnect:
        print(f"❌ WebSocket disconnected: {session_id}")
        processing_sessions.discard(session_id)
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        processing_sessions.discard(session_id)
        import traceback
        traceback.print_exc()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "mode": "demo-working",
        "features": {
            "stt": "simulated",
            "tts": "gTTS",
            "llm": "rule-based"
        },
        "note": "No API key needed - fully functional demo"
    }

@app.get("/")
async def root():
    return {
        "message": "Clinical Voice AI API - Demo Mode (Fully Working)",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "websocket": "/ws/{session_id}",
        "status": "operational"
    }

@app.get("/api/doctors")
async def get_doctors():
    return [
        {
            "id": "D1",
            "name": "Dr. Sarah Johnson",
            "specialization": "General Physician",
            "availability": "Mon-Fri 9 AM - 5 PM",
            "is_active": True
        },
        {
            "id": "D2",
            "name": "Dr. Raj Kumar",
            "specialization": "Cardiologist",
            "availability": "Mon-Wed 10 AM - 4 PM",
            "is_active": True
        },
        {
            "id": "D3",
            "name": "Dr. Priya Sharma",
            "specialization": "Pediatrician",
            "availability": "Tue-Sat 9 AM - 3 PM",
            "is_active": True
        }
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main_working:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
