from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI
from .config import AgentConfig
from .utils.logging import setup_logger
from .utils.metrics import PerformanceMonitor
from .utils.cache import CacheManager
from typing import Optional, Dict, Any

class BaseAgent(ABC):
    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
        self.logger = setup_logger(self.__class__.__name__)
        self.llm = ChatOpenAI(
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        self.cache = CacheManager(max_size=self.config.cache_size)
        self.monitor = PerformanceMonitor()
    
    @abstractmethod
    async def process(self, *args, **kwargs):
        """Main processing method to be implemented by specific agents"""
        pass
    
    async def _run_with_monitoring(self, func, *args, **kwargs):
        """Run a function with performance monitoring"""
        with self.monitor.track():
            result = await func(*args, **kwargs)
            return result, self.monitor.get_metrics()