from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Clinical Voice AI"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    
    # Redis
    REDIS_URL: str
    REDIS_SESSION_TTL: int = 1800  # 30 minutes
    
    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    # OpenAI
    OPENAI_API_KEY: str = "sk-demo"
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Groq
    GROQ_API_KEY: str = ""
    
    # Speech
    WHISPER_MODEL: str = "base"
    TTS_MODEL: str = "tts_models/multilingual/multi-dataset/your_tts"
    SAMPLE_RATE: int = 16000
    
    # Latency Targets (ms)
    TARGET_STT_LATENCY: int = 120
    TARGET_LLM_LATENCY: int = 200
    TARGET_TTS_LATENCY: int = 150
    TARGET_TOTAL_LATENCY: int = 450
    
    # Languages
    SUPPORTED_LANGUAGES: list = ["en", "hi", "ta"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
