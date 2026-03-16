from fastapi import WebSocket, WebSocketDisconnect
from app.services.stt import stt_service
from app.services.tts import tts_service
from app.agents.voice_agent import VoiceAgent
from app.db.redis import redis_client
from app.db.session import AsyncSessionLocal
from app.models.schemas import VoiceMessage, LatencyMetrics
import json
import base64
import time
from datetime import datetime

class VoiceWebSocketHandler:
    def __init__(self, websocket: WebSocket, session_id: str):
        self.websocket = websocket
        self.session_id = session_id
        self.agent = None
        self.db = None
        self.is_interrupted = False
    
    async def connect(self):
        """Accept WebSocket connection and initialize"""
        await self.websocket.accept()
        
        # Get or create session
        session_data = await redis_client.get_session(self.session_id)
        if not session_data:
            session_data = {
                "session_id": self.session_id,
                "patient_id": "default_patient",  # Should be authenticated
                "language": "en",
                "context": {},
                "conversation_history": []
            }
            await redis_client.set_session(self.session_id, session_data)
        
        # Initialize database session
        self.db = AsyncSessionLocal()
        
        # Initialize agent
        self.agent = VoiceAgent(
            db=self.db,
            patient_id=session_data["patient_id"],
            language=session_data["language"]
        )
    
    async def handle_messages(self):
        """Main message handling loop"""
        try:
            while True:
                # Receive message
                data = await self.websocket.receive_text()
                message = json.loads(data)
                
                if message["type"] == "audio_chunk":
                    await self.process_audio(message)
                elif message["type"] == "control":
                    await self.handle_control(message)
                
        except WebSocketDisconnect:
            await self.disconnect()
        except Exception as e:
            print(f"WebSocket error: {e}")
            await self.disconnect()
    
    async def process_audio(self, message: dict):
        """Process incoming audio chunk"""
        start_total = time.time()
        
        try:
            # Decode audio
            audio_data = base64.b64decode(message["data"])
            
            # Speech-to-Text
            start_stt = time.time()
            text, language, stt_latency = await stt_service.transcribe(audio_data)
            
            if not text:
                return
            
            # Update session language if detected
            session_data = await redis_client.get_session(self.session_id)
            if session_data["language"] != language:
                session_data["language"] = language
                self.agent.language = language
                await redis_client.set_session(self.session_id, session_data)
            
            # Send transcript to client
            await self.send_message({
                "type": "text",
                "data": text,
                "metadata": {"role": "user"}
            })
            
            # LLM Agent Processing
            start_llm = time.time()
            response_text, llm_latency = await self.agent.process(
                text,
                session_data.get("context", {})
            )
            
            # Update conversation history
            session_data["conversation_history"].append({
                "role": "user",
                "content": text,
                "timestamp": datetime.utcnow().isoformat()
            })
            session_data["conversation_history"].append({
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.utcnow().isoformat()
            })
            await redis_client.set_session(self.session_id, session_data)
            
            # Send text response
            await self.send_message({
                "type": "text",
                "data": response_text,
                "metadata": {"role": "assistant"}
            })
            
            # Text-to-Speech
            if not self.is_interrupted:
                start_tts = time.time()
                audio_bytes, tts_latency = await tts_service.synthesize(
                    response_text,
                    language
                )
                
                if audio_bytes and not self.is_interrupted:
                    # Send audio response
                    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                    await self.send_message({
                        "type": "audio_chunk",
                        "data": audio_b64,
                        "sample_rate": 16000
                    })
            
            # Calculate and send latency metrics
            total_latency = (time.time() - start_total) * 1000
            
            metrics = LatencyMetrics(
                stt_latency=stt_latency,
                llm_latency=llm_latency,
                tool_latency=0.0,  # Would be tracked in agent
                tts_latency=tts_latency if not self.is_interrupted else 0.0,
                total_latency=total_latency
            )
            
            await self.send_message({
                "type": "latency",
                "data": "",
                "metadata": metrics.dict()
            })
            
            self.is_interrupted = False
            
        except Exception as e:
            print(f"Audio processing error: {e}")
            await self.send_message({
                "type": "error",
                "data": "Failed to process audio",
                "metadata": {"error": str(e)}
            })
    
    async def handle_control(self, message: dict):
        """Handle control messages"""
        action = message["data"]
        
        if action == "interrupt":
            self.is_interrupted = True
            await self.send_message({
                "type": "control",
                "data": "interrupted",
                "metadata": {}
            })
    
    async def send_message(self, message: dict):
        """Send message to client"""
        try:
            await self.websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"Send error: {e}")
    
    async def disconnect(self):
        """Clean up on disconnect"""
        if self.db:
            await self.db.close()
        
        try:
            await self.websocket.close()
        except:
            pass
