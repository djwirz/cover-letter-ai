from abc import ABC, abstractmethod
import asyncio
from typing import Optional, Dict, Any, TypeVar, Generic, AsyncGenerator
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from app.agents.utils.logging import setup_logger
from app.agents.utils.metrics import PerformanceMonitor
from app.agents.utils.cache import CacheManager
from app.settings.config import Settings

T = TypeVar('T')

class AgentConfig(BaseModel):
    """Configuration for all agents"""
    model_name: str = Field(default="gpt-4", description="The model name for the LLM")
    temperature: float = Field(default=0.7, description="Temperature for the LLM")
    max_tokens: int = Field(default=1000, description="Maximum tokens for the LLM")
    cache_size: int = Field(default=1000, description="Cache size for the agent")
    log_level: str = Field(default="INFO", description="Logging level")
    retry_attempts: int = Field(default=3, description="Number of retry attempts")
    timeout: int = Field(default=30, description="Timeout for requests")
    
    # Optional fields that can be passed from environment
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    supabase_url: Optional[str] = Field(default=None, description="Supabase URL")
    supabase_key: Optional[str] = Field(default=None, description="Supabase key")

class BaseAgent(ABC, Generic[T]):
    """Base class for all AI agents providing common functionality"""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize the base agent with configuration
        
        Args:
            config: Optional configuration override
        """
        self.config = config or AgentConfig()
        self.logger = setup_logger(self.__class__.__name__, level=self.config.log_level)
        self.llm = ChatOpenAI(
            model_name=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            request_timeout=self.config.timeout
        )
        self.cache = CacheManager(max_size=self.config.cache_size)
        self.monitor = PerformanceMonitor()
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize agent resources"""
        if not self._initialized:
            await self.cache.initialize()
            await self.monitor.initialize()
            self._initialized = True
            self.logger.info(f"{self.__class__.__name__} initialized")

    async def close(self) -> None:
        """Clean up agent resources"""
        if self._initialized:
            await self.cache.close()
            await self.monitor.close()
            self._initialized = False
            self.logger.info(f"{self.__class__.__name__} closed")

    @abstractmethod
    async def process(self, *args, **kwargs) -> T:
        """Main processing method to be implemented by specific agents"""
        pass

    async def _run_with_monitoring(self, func: callable, *args, **kwargs) -> tuple[T, Dict[str, Any]]:
        """
        Run a function with performance monitoring and error handling
        
        Args:
            func: The function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Tuple of function result and performance metrics
            
        Raises:
            Exception: If the function fails after retries
        """
        attempt = 0
        last_error = None
        
        while attempt < self.config.retry_attempts:
            try:
                with self.monitor.track():
                    result = await func(*args, **kwargs)
                    metrics = self.monitor.get_metrics()
                    self.logger.debug(f"Operation succeeded on attempt {attempt + 1}")
                    return result, metrics
            except Exception as e:
                last_error = e
                attempt += 1
                self.logger.warning(f"Attempt {attempt} failed: {str(e)}")
                if attempt < self.config.retry_attempts:
                    await asyncio.sleep(1 * attempt)  # Exponential backoff
                    
        self.logger.error(f"Operation failed after {attempt} attempts")
        raise last_error or Exception("Unknown error occurred")

    def __enter__(self):
        raise TypeError("Use async context manager instead")

    def __exit__(self, *args):
        pass

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        if exc_type:
            self.logger.error(f"Exception occurred: {exc_val}")