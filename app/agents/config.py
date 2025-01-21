from pydantic import BaseSettings, Field

class AgentConfig(BaseSettings):
    model_name: str = "gpt-4"
    temperature: float = 0
    max_tokens: int = 1000
    chunk_size: int = 1000
    retry_attempts: int = 3
    cache_enabled: bool = True
    cache_size: int = 1000
    log_level: str = "INFO"
    
    class Config:
        env_prefix = "AGENT_"