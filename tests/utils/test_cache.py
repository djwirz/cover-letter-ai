"""Tests for cache utilities."""
from app.utils.cache import CacheManager

def test_cache_operations():
    cache = CacheManager()
    cache.set("test", "value")
    assert cache.get("test") == "value" 