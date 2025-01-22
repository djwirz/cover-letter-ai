"""Cache utilities for the application."""

class CacheManager:
    def __init__(self):
        self._cache = {}

    def get(self, key: str):
        return self._cache.get(key)

    def set(self, key: str, value: any):
        self._cache[key] = value 