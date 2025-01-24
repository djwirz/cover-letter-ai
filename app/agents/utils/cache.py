from typing import Dict, Any, Optional
from functools import lru_cache
import asyncio
from app.agents.utils.logging import setup_logger

logger = setup_logger("CacheManager")

class CacheManager:
    """Thread-safe caching implementation for agents"""
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize the cache manager
        
        Args:
            max_size: Maximum number of items to cache
        """
        self.max_size = max_size
        self._cache = {}
        self._lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize cache resources"""
        if not self._initialized:
            self._cache = lru_cache(maxsize=self.max_size)(self._get_item)
            self._initialized = True
            logger.info("Cache initialized")

    async def close(self) -> None:
        """Clean up cache resources"""
        if self._initialized:
            self._cache.cache_clear()
            self._initialized = False
            logger.info("Cache cleared")

    def _get_item(self, key: str) -> Optional[Dict[str, Any]]:
        """Internal cache getter"""
        return None

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get an item from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        async with self._lock:
            return self._cache(key)

    async def set(self, key: str, value: Dict[str, Any]) -> None:
        """
        Set an item in cache
        
        Args:
            key: Cache key
            value: Value to cache
        """
        async with self._lock:
            self._cache.cache_put(key, value)
            logger.debug(f"Cached item with key: {key}")

    async def clear(self) -> None:
        """Clear all cached items"""
        async with self._lock:
            self._cache.cache_clear()
            logger.info("Cache cleared")