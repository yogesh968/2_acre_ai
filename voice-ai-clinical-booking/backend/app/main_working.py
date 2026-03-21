import asyncio
import base64
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional
import io
from groq import Groq
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from gtts import gTTS
from app.core.config import get_settings
from app.services.stt import stt_service
from app.services.tts import tts_service
from dotenv import load_dotenv

# Load environment variables explicitly
load_dotenv()

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    print("🚀 Starting Clinical Voice AI application (Demo Mode)")
    
    # Load models
    try:
        stt_service.load_model()
    except Exception as e:
        print(f"⚠️ Warning: Could not pre-load Whisper model: {e}")

    print(f"📍 Server running on http://localhost:8000")
    print(f"🎤 Voice input: Enabled (ElevenLabs/Whisper)")
    print(f"🔊 Voice output: Enabled (ElevenLabs/Fallback)")
    
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

# Multi-language rule-based responses
RESPONSES = {
    "en": {
        "greeting": "Hello! I'm your medical appointment assistant. I can help you book, reschedule, or cancel appointments. How can I assist you today?",
        "booking_sarah": "Great! I can help you book an appointment with Dr. Sarah Johnson, our General Physician. She's available Monday through Friday, 9 AM to 5 PM. What date and time would work best for you?",
        "booking_raj": "Perfect! Dr. Raj Kumar, our Cardiologist, is available Monday through Wednesday, 10 AM to 4 PM. When would you like to schedule your appointment?",
        "booking_priya": "Excellent! Dr. Priya Sharma, our Pediatrician, is available Tuesday through Saturday, 9 AM to 3 PM. What date and time would you prefer?",
        "booking_general": "I'd be happy to help you book an appointment. We have three doctors available: Dr. Sarah Johnson (General Physician), Dr. Raj Kumar (Cardiologist), and Dr. Priya Sharma (Pediatrician). Which doctor would you like to see?",
        "time_noted": "Perfect! I've noted your preferred time. To complete your booking, may I know the reason for your visit? This helps the doctor prepare for your appointment.",
        "success": "Thank you! Your appointment has been successfully booked. You'll receive a confirmation message shortly. Is there anything else I can help you with?",
        "cancel": "I understand you'd like to cancel an appointment. Could you please provide your appointment ID or the date of your appointment?",
        "reschedule": "I can help you reschedule your appointment. What's your current appointment date, and when would you like to move it to?",
        "check": "Let me check your appointments. You have one upcoming appointment with Dr. Sarah Johnson on January 15th at 10 AM. Would you like to modify this appointment?",
        "thanks": "You're very welcome! If you need any assistance with appointments in the future, feel free to reach out. Take care!",
        "goodbye": "Goodbye! Have a great day and stay healthy!",
        "default": "I'm here to help with medical appointments. You can book a new appointment, reschedule an existing one, or cancel an appointment. What would you like to do?"
    },
    "hi": {
        "greeting": "नमस्ते! मैं आपका मेडिकल अपॉइंटमेंट असिस्टेंट हूँ। मैं अपॉइंटमेंट बुक करने, पुनर्निर्धारित करने या रद्द करने में आपकी मदद कर सकता हूँ। मैं आज आपकी कैसे मदद कर सकता हूँ?",
        "booking_sarah": "बहुत अच्छा! मैं जनरल फिजिशियन डॉ. सारा जॉनसन के साथ अपॉइंटमेंट बुक करने में आपकी मदद कर सकता हूँ। वह सोमवार से शुक्रवार सुबह 9 बजे से शाम 5 बजे तक उपलब्ध हैं। आपके लिए सबसे अच्छा तारीख और समय क्या होगा?",
        "booking_raj": "बिल्कुल! हमारे कार्डियोलॉजिस्ट डॉ. राज कुमार सोमवार से बुधवार सुबह 10 बजे से शाम 4 बजे तक उपलब्ध हैं। आप अपना अपॉइंटमेंट कब निर्धारित करना चाहेंगे?",
        "booking_priya": "बेहतरीन! हमारी पीडियाट्रिशियन डॉ. प्रिया शर्मा मंगलवार से शनिवार सुबह 9 बजे से दोपहर 3 बजे तक उपलब्ध हैं। आप कौन से तारीख और समय को पसंद करेंगे?",
        "booking_general": "मुझे अपॉइंटमेंट बुक करने में आपकी मदद करने में खुशी होगी। हमारे पास तीन डॉक्टर उपलब्ध हैं: डॉ. सारा जॉनसन (जनरल फिजिशियन), डॉ. राज कुमार (कार्डियोलॉजिस्ट), और डॉ. प्रिया शर्मा (पीडियाट्रिशियन)। आप किस डॉक्टर को देखना चाहेंगे?",
        "time_noted": "बढ़िया! मैंने आपके पसंदीदा समय को नोट कर लिया है। आपकी बुकिंग को पूरा करने के लिए, क्या मैं आपकी मुलाकात का कारण जान सकता हूँ? इससे डॉक्टर को आपकी अपॉइंटमेंट के लिए तैयारी करने में मदद मिलती है।",
        "success": "धन्यवाद! आपका अपॉइंटमेंट सफलतापूर्वक बुक हो गया है। आपको जल्द ही एक पुष्टिकरण संदेश प्राप्त होगा। क्या मैं आपकी किसी और चीज़ में मदद कर सकता हूँ?",
        "cancel": "मैं समझता हूँ कि आप अपॉइंटमेंट रद्द करना चाहते हैं। क्या आप कृपया अपनी अपॉइंटमेंट आईडी या अपॉइंटमेंट की तारीख बता सकते हैं?",
        "reschedule": "मैं अपॉइंटमेंट को पुनर्निर्धारित करने में आपकी मदद कर सकता हूँ। आपकी वर्तमान अपॉइंटमेंट की तारीख क्या है, और आप इसे कब बदलना चाहेंगे?",
        "check": "मुझे आपके अपॉइंटमेंट चेक करने दें। डॉ. सारा जॉनसन के साथ 15 जनवरी को सुबह 10 बजे आपका एक आगामी अपॉइंटमेंट है। क्या आप इस अपॉइंटमेंट में बदलाव करना चाहेंगे?",
        "thanks": "आपका बहुत स्वागत है! यदि आपको भविष्य में अपॉइंटमेंट के लिए किसी सहायता की आवश्यकता हो, तो बेझिझक संपर्क करें। अपना ख्याल रखें!",
        "goodbye": "अलविदा! आपका दिन शुभ हो और स्वस्थ रहें!",
        "default": "मैं यहाँ मेडिकल अपॉइंटमेंट में मदद करने के लिए हूँ। आप नया अपॉइंटमेंट बुक कर सकते हैं, मौजूदा अपॉइंटमेंट को पुनर्निर्धारित कर सकते हैं, या अपॉइंटमेंट रद्द कर सकते हैं। आप क्या करना चाहेंगे?"
    },
    "ta": {
        "greeting": "வணக்கம்! நான் உங்கள் மருத்துவ சந்திப்பு உதவியாளர். சந்திப்புகளை முன்பதிவு செய்ய, மாற்றியமைக்க அல்லது ரத்து செய்ய நான் உங்களுக்கு உதவ முடியும். இன்று நான் உங்களுக்கு எப்படி உதவ முடியும்?",
        "booking_sarah": "மிகவும் நன்று! எமது பொது மருத்துவர் டாக்டர் சாரா ஜான்சனுடன் சந்திப்பை முன்பதிவு செய்ய நான் உங்களுக்கு உதவ முடியும். அவர் திங்கள் முதல் வெள்ளி வரை காலை 9 மணி முதல் மாலை 5 மணி வரை இருப்பார். உங்களுக்கு எந்த தேதி மற்றும் நேரம் வசதியாக இருக்கும்?",
        "booking_raj": "நிச்சயமாக! எமது இதய சிகிச்சை நிபுணர் டாக்டர் ராஜ் குமார் திங்கள் முதல் புதன் வரை காலை 10 மணி முதல் மாலை 4 மணி வரை இருப்பார். உங்கள் சந்திப்பை எப்போது திட்டமிட விரும்புகிறீர்கள்?",
        "booking_priya": "சிறப்பு! எமது குழந்தை நல மருத்துவர் டாக்டர் பிரியா சர்மா செவ்வாய் முதல் சனி வரை காலை 9 மணி முதல் மாலை 3 மணி வரை இருப்பார். நீங்கள் எந்த தேதி மற்றும் நேரத்தை விரும்புவீர்கள்?",
        "booking_general": "சந்திப்பை முன்பதிவு செய்ய உங்களுக்கு உதவுவதில் நான் மகிழ்ச்சியடைகிறேன். எங்களிடம் மூன்று மருத்துவர்கள் உள்ளனர்: டாக்டர் சாரா ஜான்சன் (பொது மருத்துவர்), டாக்டர் ராஜ் குமார் (இதய சிகிச்சை நிபுணர்), மற்றும் டாக்டர் பிரியா சர்மா (குழந்தை நல மருத்துவர்). நீங்கள் எந்த மருத்துவரைப் பார்க்க விரும்புகிறீர்கள்?",
        "time_noted": "மிகவும் நன்று! நீங்கள் விரும்பிய நேரத்தை நான் குறித்துக்கொண்டேன். உங்கள் முன்பதிவை முடிக்க, உங்கள் வருகைக்கான காரணத்தை நான் தெரிந்து கொள்ளலாமா? இது மருத்துவர் உங்கள் சந்திப்புக்குத் தயாராக உதவும்.",
        "success": "நன்றி! உங்கள் சந்திப்பு வெற்றிகரமாக முன்பதிவு செய்யப்பட்டுள்ளது. விரைவில் உங்களுக்கு உறுதிப்படுத்தல் செய்தி வரும். நான் உங்களுக்கு வேறு ஏதேனும் உதவ முடியுமா?",
        "cancel": "நீங்கள் ஒரு சந்திப்பை ரத்து செய்ய விரும்புகிறீர்கள் என்று எனக்குப் புரிகிறது. உங்கள் சந்திப்பு ஐடி அல்லது சந்திப்பு தேதியை வழங்க முடியுமா?",
        "reschedule": "உங்கள் சந்திப்பை மாற்றியமைக்க நான் உங்களுக்கு உதவ முடியும். உங்கள் தற்போதைய சந்திப்பு தேதி என்ன, அதை எப்போது மாற்ற விரும்புகிறீர்கள்?",
        "check": "உங்கள் சந்திப்புகளைச் சரிபார்க்கிறேன். ஜனவரி 15 காலை 10 மணிக்கு டாக்டர் சாரா ஜான்சனுடன் உங்களுக்கு ஒரு சந்திப்பு உள்ளது. இந்த சந்திப்பை மாற்ற விரும்புகிறீர்களா?",
        "thanks": "மிக்க நன்றி! எதிர்காலத்தில் சந்திப்புகளுக்கு ஏதேனும் உதவி தேவைப்பட்டால், தயங்காமல் தொடர்பு கொள்ளுங்கள். உடலை நன்றாகப் பார்த்துக் கொள்ளுங்கள்!",
        "goodbye": "சென்று வருகிறேன்! இனிய நாளாக அமையட்டும், ஆரோக்கியமாக இருங்கள்!",
        "default": "மருத்துவ சந்திப்புகளுக்கு உதவ நான் இங்கு இருக்கிறேன். நீங்கள் ஒரு புதிய சந்திப்பு முன்பதிவு செய்யலாம், ஏற்கனவே உள்ள சந்திப்பை மாற்றியமைக்கலாம் அல்லது சந்திப்பு ரத்து செய்யலாம். நீங்கள் என்ன செய்ய விரும்புகிறீர்கள்?"
    }
}

# Initializing Groq client
groq_client = None
if settings.GROQ_API_KEY:
    try:
        from groq import Groq
        groq_client = Groq(api_key=settings.GROQ_API_KEY)
        print("✅ Groq LLM initialized")
    except Exception as e:
        print(f"❌ Groq initialization failed: {e}")

def get_ai_response(user_text: str, session: dict) -> str:
    """Natural clinical booking conversation using LLM"""
    language = session.get("language", "en")
    history = session.get("conversation_history", [])
    
    # Check for Groq first for natural conversation
    if groq_client:
        try:
            # Ensure session has history
            if "conversation_history" not in session:
                session["conversation_history"] = []
                
            # Prepare messages
            system_prompt = f"""You are Nova, a helpful and professional clinical appointment assistant.
            You help patients book, reschedule, or cancel appointments with doctors.
            
            Doctors available:
            - Dr. Sarah Johnson (General Practitioner)
            - Dr. Raj Kumar (Cardiologist)
            - Dr. Priya Sharma (Pediatrician)
            
            Current state: {session.get('state', 'idle')}
            Current doctor: {session.get('doctor', 'none')}
            
            Voice Interaction Guidelines:
            - Keep responses clear and very concise (maximum 2 short sentences).
            - Do NOT repeat the same greeting if you've already introduced yourself.
            - If the user's input is unclear, ask for clarification politely.
            - Focus on moving the process forward: ask for doctor choice, then date/time, then reason.
            
            Responding in: {language}
            Important: Use native {language} script directly.
            """
            
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add recent history (last 10 rounds)
            for msg in history[-10:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Add current user message
            messages.append({"role": "user", "content": user_text})
            
            print(f"🧠 Sending to Groq (History: {len(history)} msgs): '{user_text[0:30]}...'")
            
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            
            ai_text = completion.choices[0].message.content.strip()
            
            # Basic state inference from LLM response (simple version)
            # This helps keep the fallback logic in sync if needed
            ai_text_lower = ai_text.lower()
            if any(w in ai_text_lower for w in ["sarah", "johnson"]): session["doctor"] = "Dr. Sarah Johnson"
            if any(w in ai_text_lower for w in ["raj", "kumar"]): session["doctor"] = "Dr. Raj Kumar"
            if any(w in ai_text_lower for w in ["priya", "sharma"]): session["doctor"] = "Dr. Priya Sharma"
            
            return ai_text
            
        except Exception as e:
            print(f"❌ LLM Error (Groq): {e}. Falling back to rules.")

    # Fallback to rule-based if Groq fails
    text_lower = user_text.lower()
    state = session.get("state", "idle")
    resp = RESPONSES.get(language, RESPONSES["en"])
    
    # 1. Check for cancellation or reset keywords (handled globally)
    if any(word in text_lower for word in ['cancel', 'delete', 'ரத்து', 'रद्द', 'wait', 'stop', 'back']):
        session["state"] = "idle"
        session["doctor"] = None
        return resp["cancel"]

    # 2. Simplified State-based logic for fallback
    if state == "idle":
        if any(word in text_lower for word in ['hello', 'hi', 'hey', 'good morning', 'नमस्ते', 'வணக்கம்']):
            return resp["greeting"]
        
        if any(word in text_lower for word in ['book', 'schedule', 'appointment', 'बुकिंग', 'முன்பதிவு']):
            session["state"] = "booking"
            return resp["booking_general"]
        
        return resp["default"]

    elif state == "booking":
        session["state"] = "completed"
        return resp["success"]

    return resp["default"]

async def text_to_speech(text: str, language: str = "en") -> bytes:
    """Convert text to speech using TTS service"""
    audio_bytes, latency = await tts_service.synthesize(text, language)
    return audio_bytes

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for voice communication"""
    await websocket.accept()
    print(f"✅ WebSocket connected: {session_id}")
    
    if session_id not in sessions:
        sessions[session_id] = {
            "language": "en",
            "conversation_history": [],
            "state": "idle",
            "doctor": None,
            "last_processed_text": "",
            "last_processed_time": 0
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
                session = sessions[session_id]
                history_len = len(session.get("conversation_history", []))
                print(f"📝 Processing audio for session {session_id} (History size: {history_len})")
                
                start_time = time.time()
                
                # Real STT using Whisper service
                audio_data = base64.b64decode(message["data"])
                user_text, detected_lang, stt_latency = await stt_service.transcribe(audio_data)
                
                # Filter out silence, noise, or hallucinated repetitive phrases
                hallucination_phrases = ["thanks for watching", "thank you", "you", "...]", "thank you for watching", "watching", "subscribe", "please subscribe"]
                clean_text = user_text.strip().lower().strip('.')
                if not user_text or len(clean_text) < 2 or clean_text in hallucination_phrases:
                    print(f"⚠️  Ignoring low-quality or noisy input: '{user_text}'")
                    processing_sessions.discard(session_id)
                    continue
                
                # Improved Echo cancellation - ignore if user text is identical to recent processed text
                # but only if it happens within a short 5-second window
                last_txt = str(session.get("last_processed_text", ""))
                last_time = float(session.get("last_processed_time", 0))
                time_since_last = time.time() - last_time
                
                if user_text.lower().strip() == last_txt.lower().strip() and time_since_last < 5:
                    print(f"🔄 Duplicate text detected within {time_since_last:.1f}s, ignoring: '{user_text}'")
                    processing_sessions.discard(session_id)
                    continue

                session["last_processed_text"] = user_text
                session["last_processed_time"] = time.time()

                history = session["conversation_history"]
                is_echo = False
                for prev in reversed(history[-3:]): # Check last 3 messages
                    if prev["role"] == "assistant":
                        prev_text = prev["content"].lower()
                        # If user text is a subset of assistant text or vice versa
                        if (len(user_text) > 10 and (user_text.lower() in prev_text or prev_text in user_text.lower())) or \
                           (len(user_text) <= 10 and user_text.lower() in prev_text):
                            is_echo = True
                            break
                
                if is_echo:
                    print(f"🔇 Echo detected, ignoring: '{user_text}'")
                    processing_sessions.discard(session_id)
                    continue

                # Auto-update language based on detection
                if detected_lang in RESPONSES and detected_lang != session["language"]:
                    session["language"] = detected_lang
                    print(f"🌐 Language auto-switched to: {detected_lang}")

                current_lang = session["language"]
                
                # Send transcript back
                await websocket.send_text(json.dumps({
                    "type": "text",
                    "data": user_text,
                    "metadata": {"role": "user", "detected_lang": detected_lang}
                }))
                
                # Get AI response
                llm_start = time.time()
                assistant_text = get_ai_response(user_text, sessions[session_id])
                llm_latency = (time.time() - llm_start) * 1000
                
                print(f"🤖 AI Response ({llm_latency:.0f}ms) [{current_lang}]: {assistant_text}")
                
                # Send text response
                await websocket.send_text(json.dumps({
                    "type": "text",
                    "data": assistant_text,
                    "metadata": {"role": "assistant"}
                }))
                
                # Generate speech
                tts_start = time.time()
                audio_bytes = await text_to_speech(assistant_text, current_lang)
                tts_latency = (time.time() - tts_start) * 1000
                
                if audio_bytes:
                    print(f"🔊 TTS generated ({tts_latency:.0f}ms), sending audio...")
                    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                    await websocket.send_text(json.dumps({
                        "type": "audio_chunk",
                        "data": audio_b64,
                        "sample_rate": 44100,
                        "metadata": {"format": "mp3"}
                    }))
                    print(f"✅ Audio sent to client")
                
                # Send latency metrics
                total_latency = (time.time() - start_time) * 1000
                await websocket.send_text(json.dumps({
                    "type": "latency",
                    "data": "",
                    "metadata": {
                        "stt_latency": stt_latency,
                        "llm_latency": llm_latency,
                        "tool_latency": 0.0,
                        "tts_latency": tts_latency,
                        "total_latency": total_latency,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }))
                
                # Store in conversation history
                sessions[session_id]["conversation_history"].append({"role": "user", "content": user_text, "timestamp": datetime.utcnow().isoformat()})
                sessions[session_id]["conversation_history"].append({"role": "assistant", "content": assistant_text, "timestamp": datetime.utcnow().isoformat()})
                
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
        if session_id in processing_sessions:
            processing_sessions.discard(session_id)
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        if session_id in processing_sessions:
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
            "stt": "ElevenLabs/Whisper",
            "tts": "ElevenLabs/Fallback",
            "llm": "groq-llama-3.3" if groq_client else "rule-based",
            "groq_status": "initialized" if groq_client else "missing_key"
        }
    }

@app.get("/")
async def root():
    return {
        "message": "Clinical Voice AI API - Demo Mode",
        "status": "operational"
    }

@app.get("/api/doctors")
async def get_doctors():
    return [
        {"id": "D1", "name": "Dr. Sarah Johnson", "specialization": "General Physician"},
        {"id": "D2", "name": "Dr. Raj Kumar", "specialization": "Cardiologist"},
        {"id": "D3", "name": "Dr. Priya Sharma", "specialization": "Pediatrician"}
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main_working:app", host="0.0.0.0", port=8000, reload=True)
