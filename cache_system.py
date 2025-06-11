from typing import Any, Dict, List, Optional, Tuple
"""
Système de cache consolidé pour Smart Patch Processor
Regroupe: DummyCache, CacheEntry, CacheStats, CacheStrategy, SmartCache
"""

import logging
import threading
from pathlib import Path
from datetime import datetime
from collections import OrderedDict
from enum import Enum
from dataclasses import dataclass, field
import hashlib

# ============================================================================
# TYPES ET ENUMS
# ============================================================================

class CacheStrategy(Enum):
    """Stratégies de cache disponibles"""
    LRU = "lru"
    LFU = "lfu" 
    TTL = "ttl"
    HYBRID = "hybrid"
    ADAPTIVE = "adaptive"

@dataclass
class CacheStats:
    """Statistiques de performance du cache"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_entries: int = 0
    hit_rate: float = 0.0
    
    def update_hit_rate(self):
        total = self.hits + self.misses
        self.hit_rate = (self.hits / total * 100) if total > 0 else 0.0

@dataclass
class CacheEntry:
    """Entrée de cache avec métadonnées"""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    file_mtime: Optional[float] = None
    size_bytes: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    
    @property
    def is_expired(self) -> bool:
        if self.ttl_seconds is None:
            return False
        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl_seconds
    
    def touch(self):
        self.last_accessed = datetime.now()
        self.access_count += 1

# ============================================================================
# IMPLEMENTATIONS DE CACHE
# ============================================================================

class DummyCache:
    """Cache factice qui ne cache rien (fallback)"""
    def put(self, key: str, value: Any, **kwargs) -> bool: 
        return False
    def get(self, key: str) -> None: 
        return None
    def clear(self): 
        pass

class SmartCache:
    """Cache intelligent intégré pour Smart Patch Processor"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self.stats = CacheStats()
        self.logger = logging.getLogger('smart_patch_processor.cache')
    
    def put(self, key: str, value: Any, ttl: Optional[int] = None, file_path: Optional[Path] = None) -> bool:
        with self._lock:
            effective_ttl = ttl or self.default_ttl
            file_mtime = file_path.stat().st_mtime if file_path and file_path.exists() else None
            
            entry = CacheEntry(
                key=key, value=value, created_at=datetime.now(),
                last_accessed=datetime.now(), access_count=1,
                ttl_seconds=effective_ttl, file_mtime=file_mtime
            )
            
            self._cache[key] = entry
            self._enforce_size_limits()
            return True
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self.stats.misses += 1
                return None
            
            if entry.is_expired:
                self._cache.pop(key)
                self.stats.misses += 1
                return None
            
            entry.touch()
            self._cache.move_to_end(key)
            self.stats.hits += 1
            self.stats.update_hit_rate()
            return entry.value
    
    def _enforce_size_limits(self):
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)
            self.stats.evictions += 1
    
    def clear(self):
        with self._lock:
            self._cache.clear()
            self.stats = CacheStats()

# ============================================================================
# GESTIONNAIRE GLOBAL
# ============================================================================

class CacheManager:
    """Gestionnaire global des caches"""
    
    def __init__(self, config):
        self.config = config
        cache_config = config.get_section('cache') if hasattr(config, 'get_section') else {}
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
