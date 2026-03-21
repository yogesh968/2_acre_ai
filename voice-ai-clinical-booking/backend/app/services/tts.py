from gtts import gTTS
import io
from app.core.config import get_settings
import time
from typing import Tuple
import asyncio
import concurrent.futures

settings = get_settings()

# Try to import ElevenLabs (optional)
try:
    from elevenlabs import ElevenLabs
    HAS_ELEVENLABS = True
except ImportError:
    HAS_ELEVENLABS = False

class TextToSpeechService:
    def __init__(self):
        self.client = None
        self.elevenlabs_working = False
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        
        # Initialize ElevenLabs client if key is present and module available
        if HAS_ELEVENLABS and settings.ELEVENLABS_API_KEY:
            try:
                self.client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
                print("✅ ElevenLabs TTS client initialized (will test on first call)")
            except Exception as e:
                print(f"❌ Failed to initialize ElevenLabs client: {e}")
        
        print("✅ gTTS (Google Text-to-Speech) ready as primary/fallback TTS")
    
    def _gtts_synthesize_sync(self, text: str, language: str) -> bytes:
        """Google TTS synchronous synthesis - reliable and free"""
        lang_map = {
            "en": "en",
            "hi": "hi", 
            "ta": "ta",
            "eng": "en",
            "hin": "hi",
            "tam": "ta",
        }
        gtts_lang = lang_map.get(language, "en")
        
        tts = gTTS(text=text, lang=gtts_lang)
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        return buffer.getvalue()

    def _elevenlabs_synthesize_sync(self, text: str, language: str) -> bytes:
        """ElevenLabs synchronous synthesis (requires paid plan)"""
        # Use a common pre-made voice ID
        voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel
        
        audio_generator = self.client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        return b"".join(audio_generator)

    async def synthesize(self, text: str, language: str = "en") -> Tuple[bytes, float]:
        """
        Convert text to speech.
        Uses gTTS (Google TTS) as the primary engine.
        ElevenLabs is tried only if previously confirmed working.
        Returns: (audio_bytes_mp3, latency_ms)
        """
        start_time = time.time()
        loop = asyncio.get_event_loop()
        
        # Option 1: Try ElevenLabs if we know it works
        if self.client and self.elevenlabs_working:
            try:
                audio_bytes = await loop.run_in_executor(
                    self.executor,
                    self._elevenlabs_synthesize_sync,
                    text,
                    language
                )
                latency = (time.time() - start_time) * 1000
                print(f"🔊 ElevenLabs TTS: {len(audio_bytes)} bytes ({latency:.0f}ms)")
                return audio_bytes, latency
            except Exception as e:
                print(f"⚠️ ElevenLabs TTS failed: {e}")
                self.elevenlabs_working = False
                start_time = time.time()
        
        # Option 2: gTTS (primary engine - always works)
        try:
            audio_bytes = await loop.run_in_executor(
                self.executor,
                self._gtts_synthesize_sync,
                text,
                language
            )
            latency = (time.time() - start_time) * 1000
            print(f"🔊 gTTS: {len(audio_bytes)} bytes ({latency:.0f}ms) [lang={language}]")
            return audio_bytes, latency
        except Exception as e:
            print(f"❌ gTTS Error: {e}")
            return b"", 0.0

tts_service = TextToSpeechService()
