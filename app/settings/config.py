from pydantic_settings import BaseSettings
from pydantic import Field, model_validator
from dotenv import load_dotenv
from typing import Dict, Any, Optional
import os

# Load environment variables
load_dotenv()

class AgentSettings(BaseSettings):
    """Configuration for AI agents"""
    model_name: str = Field("gpt-4", env="AGENT_MODEL_NAME")
    temperature: float = Field(0.7, ge=0, le=1)
    max_tokens: int = Field(1000, gt=0)
    cache_size: int = Field(1000, gt=0)
    log_level: str = Field("INFO", env="AGENT_LOG_LEVEL")
    retry_attempts: int = Field(3, gt=0)
    timeout: int = Field(30, gt=0)

class DatabaseSettings(BaseSettings):
    """Database configuration"""
    url: str = Field("sqlite+aiosqlite:///./test.db", env="DATABASE_URL")
    pool_size: int = Field(10, gt=0)
    max_overflow: int = Field(5, ge=0)
    echo: bool = Field(False, env="DATABASE_ECHO")

class VectorStoreSettings(BaseSettings):
    """Vector store configuration"""
    collection: str = Field("vectors", env="VECTOR_COLLECTION")
    chunk_size: int = Field(1000, gt=0)
    chunk_overlap: int = Field(200, ge=0)
    embedding_dim: int = Field(1536, gt=0)

class Settings(BaseSettings):
    """Application-wide settings"""
    debug: bool = Field(False, env="DEBUG")
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_key: str = Field(..., env="SUPABASE_KEY")

    # Sub-configurations
    agents: AgentSettings = AgentSettings()
    database: DatabaseSettings = DatabaseSettings()
    vector_store: VectorStoreSettings = VectorStoreSettings()

    @model_validator(mode='after')
    def validate_settings(self) -> 'Settings':
        """Validate and transform settings"""
        if self.debug:
            self.agents.log_level = "DEBUG"
            self.database.echo = True
            
        return self

    @property
    def OPENAI_MODEL(self) -> str:
        """Get OpenAI model name."""
        return self.agents.model_name

    @property
    def OPENAI_TEMPERATURE(self) -> float:
        """Get OpenAI temperature."""
        return self.agents.temperature

    @property
    def debug_mode(self) -> bool:
        """Get debug mode."""
        return self.debug

    @property
    def OPENAI_MODEL(self) -> str:
        """Get OpenAI model name."""
        return self.agents.model_name

    @property
    def OPENAI_TEMPERATURE(self) -> float:
        """Get OpenAI temperature."""
        return self.agents.temperature

    @property
    def database_url(self) -> str:
        """Get database URL."""
        return self.database.url

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Singleton settings instance
settings = Settings()

# Validate settings on import
if not settings.openai_api_key:
    raise ValueError("OPENAI_API_KEY is required")