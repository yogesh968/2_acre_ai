from elevenlabs.client import ElevenLabs
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=api_key)

try:
    voices = client.voices.get_all()
    print("Available Voices:")
    for v in voices.voices:
        print(f"- {v.name}: {v.voice_id} (Category: {v.category})")
except Exception as e:
    print(f"Error: {e}")
