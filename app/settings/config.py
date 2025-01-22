from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Explicitly load .env file
load_dotenv()

class Config:
    """Application configuration."""
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    # Database settings
    DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "coverletter")

    # Vector store settings
    VECTOR_COLLECTION = os.getenv("VECTOR_COLLECTION", "vectors")

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    SUPABASE_URL: str
    SUPABASE_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Add some debug printing to verify
settings = Settings()
print(f"Loaded OPENAI_API_KEY: {'set' if settings.OPENAI_API_KEY else 'not set'}")