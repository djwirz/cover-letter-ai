from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Explicitly load .env file
load_dotenv()

class Settings(BaseSettings):
    # OpenAI settings
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_TEMPERATURE: float = 0.7
    
    # Database settings
    DATABASE_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "coverletter"
    
    # Vector store settings
    VECTOR_COLLECTION: str = "vectors"
    
    # Supabase settings
    SUPABASE_URL: str
    SUPABASE_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
settings = Settings()

# Add some debug printing to verify
print(f"Loaded OPENAI_API_KEY: {'set' if settings.OPENAI_API_KEY else 'not set'}")