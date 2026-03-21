import whisper
import numpy as np
import io
import soundfile as sf
from app.core.config import get_settings
import time
from typing import Tuple
import asyncio
import concurrent.futures
from elevenlabs import ElevenLabs

settings = get_settings()

class SpeechToTextService:
    def __init__(self):
        self.model = None
        self.client = None
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        
        # Initialize ElevenLabs client if key is present
        if settings.ELEVENLABS_API_KEY:
            try:
                self.client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
                print("✅ ElevenLabs STT client initialized")
            except Exception as e:
                print(f"❌ Failed to initialize ElevenLabs STT client: {e}")
    
    def load_model(self):
        """Load Whisper model into memory (Fallback)"""
        if self.model is None:
            try:
                print(f"⏳ Loading Whisper model ({settings.WHISPER_MODEL})...")
                self.model = whisper.load_model(settings.WHISPER_MODEL)
                print("✅ Whisper model loaded")
            except Exception as e:
                print(f"❌ Failed to load Whisper model: {e}")
    
    def _transcribe_sync(self, audio_array) -> Tuple[str, str]:
        """Synchronous transcription (Local Fallback)"""
        if self.model:
            result = self.model.transcribe(
                audio_array,
                language=None,  # Auto-detect
                task="transcribe",
                fp16=False
            )
            return result["text"].strip(), result["language"]
        return "", "en"

    def _elevenlabs_transcribe_sync(self, audio_data: bytes) -> Tuple[str, str]:
        """ElevenLabs synchronous transcription"""
        try:
            # ElevenLabs expects a file-like object
            audio_file = io.BytesIO(audio_data)
            
            transcription = self.client.speech_to_text.convert(
                file=audio_file,
                model_id="scribe_v1", # scribe_v2 might be better if available
            )
            
            # The return value has .text and .language_code (if detected)
            text = transcription.text.strip()
            # ElevenLabs returns language_code like 'eng', Whisper returns 'en'
            language = getattr(transcription, 'language_code', 'en')
            if language == 'eng': language = 'en'
            elif language == 'hin': language = 'hi'
            elif language == 'tam': language = 'ta'
            
            return text, language
        except Exception as e:
            print(f"ElevenLabs STT error: {e}")
            raise e
    
    async def transcribe(self, audio_data: bytes) -> Tuple[str, str, float]:
        """
        Transcribe audio to text and detect language
        Returns: (text, language, latency_ms)
        """
        start_time = time.time()
        
        # Try ElevenLabs first
        if self.client:
            try:
                loop = asyncio.get_event_loop()
                text, language = await loop.run_in_executor(
                    self.executor,
                    self._elevenlabs_transcribe_sync,
                    audio_data
                )
                latency = (time.time() - start_time) * 1000
                return text, language, latency
            except Exception as e:
                print(f"⚠️ ElevenLabs STT failed, falling back to Whisper: {e}")
                start_time = time.time() # Reset for fallback
        
        # Fallback to Whisper
        try:
            # Convert audio bytes to numpy array
            audio_array, sample_rate = sf.read(io.BytesIO(audio_data))
            
            # Resample if needed
            if sample_rate != 16000:
                try:
                    import librosa
                    audio_array = librosa.resample(
                        audio_array,
                        orig_sr=sample_rate,
                        target_sr=16000
                    )
                except ImportError:
                    pass # Continue anyway if librosa is missing
            
            # Ensure mono
            if len(audio_array.shape) > 1:
                audio_array = audio_array.mean(axis=1)
            
            # Transcribe in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            text, language = await loop.run_in_executor(
                self.executor,
                self._transcribe_sync,
                audio_array
            )
            
            latency = (time.time() - start_time) * 1000
            
            return text, language, latency
            
        except Exception as e:
            print(f"STT Error (Fallback): {e}")
            return "", "en", 0.0

stt_service = SpeechToTextService()
