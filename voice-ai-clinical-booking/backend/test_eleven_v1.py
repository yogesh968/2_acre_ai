from elevenlabs.client import ElevenLabs
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=api_key)

def test_tts():
    print("Testing TTS with convert method...")
    try:
        audio_gen = client.text_to_speech.convert(
            text="Hello, this is a namespaced test.",
            voice_id="Rachel",
            model_id="eleven_multilingual_v2"
        )
        audio_bytes = b"".join(audio_gen)
        print(f"✅ TTS Success! Generated {len(audio_bytes)} bytes.")
    except Exception as e:
        print(f"❌ TTS Failed: {e}")

if __name__ == "__main__":
    test_tts()
