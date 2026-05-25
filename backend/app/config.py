import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the backend application."""
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    
    # LLM Provider: "gemini" or "openai"
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
    
    # Server settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # CORS
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:3001"
        ).split(",")
        if origin.strip()
    ]
    
    # Log simulation settings
    LOG_REFRESH_INTERVAL_MS = int(os.getenv("LOG_REFRESH_INTERVAL_MS", 2000))
    MAX_LOGS_TO_KEEP = int(os.getenv("MAX_LOGS_TO_KEEP", 100))
    
    # Validate required configuration
    @classmethod
    def validate(cls):
        if cls.LLM_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required when LLM_PROVIDER is 'gemini'")
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER is 'openai'")
        if cls.LLM_PROVIDER not in ["gemini", "openai"]:
            raise ValueError("LLM_PROVIDER must be either 'gemini' or 'openai'")
    
# Optional: validate on import (uncomment if you want immediate validation)
# Config.validate()
