from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pydantic import Field

# Explicitly load .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    openai_api_key: str = Field(..., env='OPENAI_API_KEY')
    database_url: str = Field("sqlite+aiosqlite:///./test.db", env='DATABASE_URL')
    debug_mode: bool = Field(False, env='DEBUG_MODE')
    
    # OpenAI settings
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_TEMPERATURE: float = 0.7
    
    # Database settings
    DATABASE_NAME: str = "coverletter"
    
    # Vector store settings
    VECTOR_COLLECTION: str = "vectors"
    
    # Supabase settings
    SUPABASE_URL: str
    SUPABASE_KEY: str

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
settings = Settings()

# Add some debug printing to verify
print(f"Loaded OPENAI_API_KEY: {'set' if settings.openai_api_key else 'not set'}")