"""
Cache manager for Creative Service.

Simplified caching for image/video generation results.
"""

import time
from typing import Any, Dict, Optional
from app.logger import get_logger
from app.caching.policy import get_caching_policy_loader
from collections import OrderedDict

logger = get_logger()


class CacheEntry:
    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.expires_at = time.time() + ttl
        self.size = len(str(value).encode('utf-8'))

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class CacheManager:
    def __init__(self):
        self.policy = get_caching_policy_loader().get_policy()
        self._cache: Dict[str, CacheEntry] = {}
        self._order = OrderedDict()
        logger.info("CacheManager initialized", policy=self.policy)

    def _get_ttl(self, endpoint: str) -> int:
        if not self.policy.ttl.enabled:
            return 0
        
        if endpoint in self.policy.ttl.per_endpoint_seconds:
            return self.policy.ttl.per_endpoint_seconds[endpoint]
        
        return self.policy.ttl.default_seconds

    def _evict_if_needed(self):
        max_entries = self.policy.size_limits.max_entries
        max_size_bytes = self.policy.size_limits.max_size_mb * 1024 * 1024
        current_size = sum(entry.size for entry in self._cache.values())
        
        while len(self._cache) > max_entries or current_size > max_size_bytes:
            if not self._order:
                break
            oldest_key = next(iter(self._order))
            if oldest_key in self._cache:
                entry = self._cache.pop(oldest_key)
                current_size -= entry.size
            self._order.popitem(last=False)

    def get(self, key: str) -> Optional[Any]:
        if not self.policy.enabled:
            return None
        
        if key in self._cache:
            entry = self._cache[key]
            if entry.is_expired():
                self._cache.pop(key)
                self._order.pop(key, None)
                return None
            self._order.move_to_end(key)
            logger.debug("Cache hit", key=key[:16])
            return entry.value
        
        logger.debug("Cache miss", key=key[:16])
        return None

    def set(self, key: str, value: Any, endpoint: str = "default"):
        if not self.policy.enabled:
            return
        
        ttl = self._get_ttl(endpoint)
        if key in self._cache:
            self._cache.pop(key)
            self._order.pop(key, None)
        
        entry = CacheEntry(value, ttl)
        self._cache[key] = entry
        self._order[key] = None
        self._evict_if_needed()
        logger.debug("Stored in cache", key=key[:16])

    def clear(self):
        self._cache.clear()
        self._order.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> dict:
        return {
            "enabled": self.policy.enabled,
            "current_entries": len(self._cache),
            "max_entries": self.policy.size_limits.max_entries,
            "current_size_mb": round(sum(e.size for e in self._cache.values()) / (1024 * 1024), 2),
            "max_size_mb": self.policy.size_limits.max_size_mb,
        }


_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


Simplified caching for image/video generation results.
"""

import time
from typing import Any, Dict, Optional
from app.logger import get_logger
from app.caching.policy import get_caching_policy_loader
from collections import OrderedDict

logger = get_logger()


class CacheEntry:
    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.expires_at = time.time() + ttl
        self.size = len(str(value).encode('utf-8'))

    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class CacheManager:
    def __init__(self):
        self.policy = get_caching_policy_loader().get_policy()
        self._cache: Dict[str, CacheEntry] = {}
        self._order = OrderedDict()
        logger.info("CacheManager initialized", policy=self.policy)

    def _get_ttl(self, endpoint: str) -> int:
        if not self.policy.ttl.enabled:
            return 0
        
        if endpoint in self.policy.ttl.per_endpoint_seconds:
            return self.policy.ttl.per_endpoint_seconds[endpoint]
        
        return self.policy.ttl.default_seconds

    def _evict_if_needed(self):
        max_entries = self.policy.size_limits.max_entries
        max_size_bytes = self.policy.size_limits.max_size_mb * 1024 * 1024
        current_size = sum(entry.size for entry in self._cache.values())
        
        while len(self._cache) > max_entries or current_size > max_size_bytes:
            if not self._order:
                break
            oldest_key = next(iter(self._order))
            if oldest_key in self._cache:
                entry = self._cache.pop(oldest_key)
                current_size -= entry.size
            self._order.popitem(last=False)

    def get(self, key: str) -> Optional[Any]:
        if not self.policy.enabled:
            return None
        
        if key in self._cache:
            entry = self._cache[key]
            if entry.is_expired():
                self._cache.pop(key)
                self._order.pop(key, None)
                return None
            self._order.move_to_end(key)
            logger.debug("Cache hit", key=key[:16])
            return entry.value
        
        logger.debug("Cache miss", key=key[:16])
        return None

    def set(self, key: str, value: Any, endpoint: str = "default"):
        if not self.policy.enabled:
            return
        
        ttl = self._get_ttl(endpoint)
        if key in self._cache:
            self._cache.pop(key)
            self._order.pop(key, None)
        
        entry = CacheEntry(value, ttl)
        self._cache[key] = entry
        self._order[key] = None
        self._evict_if_needed()
        logger.debug("Stored in cache", key=key[:16])

    def clear(self):
        self._cache.clear()
        self._order.clear()
        logger.info("Cache cleared")

    def get_stats(self) -> dict:
        return {
            "enabled": self.policy.enabled,
            "current_entries": len(self._cache),
            "max_entries": self.policy.size_limits.max_entries,
            "current_size_mb": round(sum(e.size for e in self._cache.values()) / (1024 * 1024), 2),
            "max_size_mb": self.policy.size_limits.max_size_mb,
        }


_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager
