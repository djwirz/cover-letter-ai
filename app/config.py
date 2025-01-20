from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Explicitly load .env file
load_dotenv()

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