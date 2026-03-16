import whisper
import numpy as np
import io
import soundfile as sf
from app.core.config import get_settings
import time
from typing import Tuple
import asyncio
import concurrent.futures

settings = get_settings()

class SpeechToTextService:
    def __init__(self):
        self.model = None
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self.load_model()
    
    def load_model(self):
        """Load Whisper model into memory"""
        self.model = whisper.load_model(settings.WHISPER_MODEL)
    
    def _transcribe_sync(self, audio_array) -> Tuple[str, str]:
        """Synchronous transcription"""
        result = self.model.transcribe(
            audio_array,
            language=None,  # Auto-detect
            task="transcribe",
            fp16=False
        )
        return result["text"].strip(), result["language"]
    
    async def transcribe(self, audio_data: bytes) -> Tuple[str, str, float]:
        """
        Transcribe audio to text and detect language
        Returns: (text, language, latency_ms)
        """
        start_time = time.time()
        
        try:
            # Convert audio bytes to numpy array
            audio_array, sample_rate = sf.read(io.BytesIO(audio_data))
            
            # Resample if needed
            if sample_rate != 16000:
                import librosa
                audio_array = librosa.resample(
                    audio_array,
                    orig_sr=sample_rate,
                    target_sr=16000
                )
            
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
            print(f"STT Error: {e}")
            return "", "en", 0.0

stt_service = SpeechToTextService()
