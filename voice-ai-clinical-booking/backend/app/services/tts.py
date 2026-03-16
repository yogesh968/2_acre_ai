from TTS.api import TTS
import io
import soundfile as sf
from app.core.config import get_settings
import time
from typing import Tuple
import asyncio
import concurrent.futures

settings = get_settings()

class TextToSpeechService:
    def __init__(self):
        self.model = None
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self.load_model()
    
    def load_model(self):
        """Load TTS model into memory"""
        try:
            self.model = TTS(settings.TTS_MODEL)
        except Exception as e:
            print(f"TTS model load error: {e}")
            # Fallback to a simpler model
            self.model = TTS("tts_models/en/ljspeech/tacotron2-DDC")
    
    def _synthesize_sync(self, text: str, language: str) -> list:
        """Synchronous synthesis"""
        return self.model.tts(text=text, language=language if language in ["en", "hi", "ta"] else "en")
    
    async def synthesize(self, text: str, language: str = "en") -> Tuple[bytes, float]:
        """
        Convert text to speech
        Returns: (audio_bytes, latency_ms)
        """
        start_time = time.time()
        
        try:
            # Generate speech in thread pool
            loop = asyncio.get_event_loop()
            wav = await loop.run_in_executor(
                self.executor,
                self._synthesize_sync,
                text,
                language
            )
            
            # Convert to bytes
            buffer = io.BytesIO()
            sf.write(buffer, wav, settings.SAMPLE_RATE, format='WAV')
            audio_bytes = buffer.getvalue()
            
            latency = (time.time() - start_time) * 1000
            
            return audio_bytes, latency
            
        except Exception as e:
            print(f"TTS Error: {e}")
            return b"", 0.0

tts_service = TextToSpeechService()
