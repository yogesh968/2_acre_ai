from elevenlabs import ElevenLabs
import os
from dotenv import load_dotenv
import io

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")
print(f"API Key present: {bool(api_key)}")

client = ElevenLabs(api_key=api_key)

def test_tts():
    print("Testing TTS...")
    try:
        # Latest SDK uses text_to_speech.convert
        audio_gen = client.text_to_speech.convert(
            text="Hello, this is a test of the clinical voice AI system.",
            voice_id="Rachel",
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        audio_bytes = b"".join(audio_gen)
        print(f"✅ TTS Success! Generated {len(audio_bytes)} bytes.")
    except Exception as e:
        print(f"❌ TTS Failed: {e}")

def test_stt():
    print("Testing STT (mocking with empty audio)...")
    # This might fail with empty audio, but let's see the error
    try:
        audio_file = io.BytesIO(b"fake audio data")
        # ElevenLabs STT needs real audio, so this will likely fail
        # but we want to see if the client is working
        print("Skipping real STT test as it needs real audio file.")
    except Exception as e:
        print(f"❌ STT Test Error: {e}")

if __name__ == "__main__":
    test_tts()
