"""Module cache_manager.py - Classe CacheManager."""

import hashlib

from dummy_cache import DummyCache
from smart_cache import SmartCache

class CacheManager:
    """Gestionnaire global des caches"""
    
    def __init__(self, config):
        self.config = config
        cache_config = config.get_section('cache')
        self.enabled = cache_config.get('enabled', True)
        
        if self.enabled:
            self.ast_cache = SmartCache(max_size=500, default_ttl=7200)
            self.detection_cache = SmartCache(max_size=200, default_ttl=3600)
            self.correction_cache = SmartCache(max_size=300, default_ttl=1800)
        else:
            self.ast_cache = self.detection_cache = self.correction_cache = DummyCache()
    
    def get_cache_key(self, prefix: str, *args) -> str:
        key_parts = [prefix] + [str(arg) for arg in args]
        key = ":".join(key_parts)
        if len(key) > 200:
            return f"{prefix}:hash:{hashlib.md5(key.encode()).hexdigest()}"
        return key
